import html
import re
from typing import Optional

from telegram import Chat, ChatPermissions, Message, Update, User
from telegram.error import BadRequest
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    Filters,
    MessageHandler,
    run_async,
)
from telegram.utils.helpers import mention_html

from AltronRobot import TIGERS, WOLVES, dispatcher
from AltronRobot.modules.connection import connected
from AltronRobot.modules.helper_funcs.alternate import send_message
from AltronRobot.modules.helper_funcs.chat_status import (
    bot_admin,
    is_user_admin,
    user_admin,
    user_admin_no_reply,
)
from AltronRobot.modules.helper_funcs.string_handling import extract_time
from AltronRobot.modules.channel import loggable
from AltronRobot.modules.sql import antiflood_sql as sql
from AltronRobot.modules.sql.approve_sql import is_approved

FLOOD_GROUP = 3


@run_async
@loggable
def check_flood(update, context) -> str:
    user = update.effective_user  # type: Optional[User]
    chat = update.effective_chat  # type: Optional[Chat]
    msg = update.effective_message  # type: Optional[Message]
    if not user:  # ignore channels
        return ""

    # ignore admins and whitelists
    if is_user_admin(chat, user.id) or user.id in WOLVES or user.id in TIGERS:
        sql.update_flood(chat.id, None)
        return ""
    # ignore approved users
    if is_approved(chat.id, user.id):
        sql.update_flood(chat.id, None)
        return
    should_ban = sql.update_flood(chat.id, user.id)
    if not should_ban:
        return ""

    try:
        getmode, getvalue = sql.get_flood_setting(chat.id)
        if getmode == 1:
            chat.kick_member(user.id)
            execstrings = "ʙᴀɴɴᴇᴅ"
        elif getmode == 2:
            chat.kick_member(user.id)
            chat.unban_member(user.id)
            execstrings = "ᴋɪᴄᴋᴇᴅ"
        elif getmode == 3:
            context.bot.restrict_chat_member(
                chat.id, user.id, permissions=ChatPermissions(can_send_messages=False)
            )
            execstrings = "ᴍᴜᴛᴇᴅ"
        elif getmode == 4:
            bantime = extract_time(msg, getvalue)
            chat.kick_member(user.id, until_date=bantime)
            execstrings = f"ʙᴀɴɴᴇᴅ ꜰᴏʀ {getvalue}"
        elif getmode == 5:
            mutetime = extract_time(msg, getvalue)
            context.bot.restrict_chat_member(
                chat.id,
                user.id,
                until_date=mutetime,
                permissions=ChatPermissions(can_send_messages=False),
            )
            execstrings = f"ᴍᴜᴛᴇᴅ ꜰᴏʀ {getvalue}"
        send_message(
            update.effective_message, f"» ʙᴇᴇᴘ ʙᴏᴏᴘ! ʙᴏᴏᴘ ʙᴇᴇᴘ!\n{execstrings}!"
        )
        return ""


    except BadRequest:
        msg.reply_text("ɪ ᴄᴀɴ'ᴛ ʀᴇꜱᴛʀɪᴄᴛ ᴘᴇᴏᴘʟᴇ ʜᴇʀᴇ, ɢɪᴠᴇ ᴍᴇ ᴘᴇʀᴍɪꜱꜱɪᴏɴꜱ ꜰɪʀꜱᴛ! ᴜɴᴛɪʟ ᴛʜᴇɴ, ɪ'ʟʟ ᴅɪꜱᴀʙʟᴇ ᴀɴᴛɪ-ꜰʟᴏᴏᴅ.")
        sql.set_flood(chat.id, 0)
        return ""


@run_async
@user_admin_no_reply
@bot_admin
def flood_button(update: Update, context: CallbackContext):
    bot = context.bot
    query = update.callback_query
    user = update.effective_user
    match = re.match(r"unmute_flooder\((.+?)\)", query.data)
    if match:
        user_id = match.group(1)
        chat = update.effective_chat.id
        try:
            bot.restrict_chat_member(
                chat,
                int(user_id),
                permissions=ChatPermissions(
                    can_send_messages=True,
                    can_send_media_messages=True,
                    can_send_other_messages=True,
                    can_add_web_page_previews=True,
                ),
            )
            update.effective_message.edit_text(
                f"» ᴜɴᴍᴜᴛᴇᴅ ʙʏ {mention_html(user.id, html.escape(user.first_name))}.",
                parse_mode="HTML",
            )
        except:
            pass


@run_async
@user_admin
@loggable
def set_flood(update, context) -> str:
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    message = update.effective_message  # type: Optional[Message]
    args = context.args

    conn = connected(context.bot, update, chat, user.id, need_admin=True)
    if conn:
        chat_id = conn
        chat_name = dispatcher.bot.getChat(conn).title
    else:
        if update.effective_message.chat.type == "private":
            send_message(
                update.effective_message,
                "» ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ɪꜱ ᴍᴇᴀɴᴛ ᴛᴏ ᴜꜱᴇ ɪɴ ɢʀᴏᴜᴘ ɴᴏᴛ ɪɴ ᴘᴍ",
            )
            return ""
        chat_id = update.effective_chat.id
        chat_name = update.effective_message.chat.title

    if len(args) >= 1:
        val = args[0].lower()
        if val in ["off", "no", "0"]:
            sql.set_flood(chat_id, 0)
            if conn:
                message.reply_text(f"» ᴀɴᴛɪꜰʟᴏᴏᴅ ʜᴀꜱ ʙᴇᴇɴ ᴅɪꜱᴀʙʟᴇᴅ ɪɴ {chat_name}.")
            else:
                message.reply_text("» ᴀɴᴛɪꜰʟᴏᴏᴅ ʜᴀꜱ ʙᴇᴇɴ ᴅɪꜱᴀʙʟᴇᴅ.")

        elif val.isdigit():
            amount = int(val)
            if amount <= 0:
                sql.set_flood(chat_id, 0)
                if conn:
                    message.reply_text(f"» ᴀɴᴛɪꜰʟᴏᴏᴅ ʜᴀꜱ ʙᴇᴇɴ ᴅɪꜱᴀʙʟᴇᴅ ɪɴ  {chat_name}.")
                else:
                    message.reply_text("» ᴀɴᴛɪꜰʟᴏᴏᴅ ʜᴀꜱ ʙᴇᴇɴ ᴅɪꜱᴀʙʟᴇᴅ.")
                return ""

            elif amount <= 3:
                send_message(
                    update.effective_message,
                    "» ᴀɴᴛɪꜰʟᴏᴏᴅ ᴍᴜꜱᴛ ʙᴇ ᴇɪᴛʜᴇʀ 0 (ᴅɪꜱᴀʙʟᴇᴅ) ᴏʀ ɴᴜᴍʙᴇʀ ɢʀᴇᴀᴛᴇʀ ᴛʜᴀɴ 3!",
                )
                return ""

            else:
                sql.set_flood(chat_id, amount)
                if conn:
                    message.reply_text(
                        "» ᴀɴᴛɪ-ꜰʟᴏᴏᴅ ʜᴀꜱ ʙᴇᴇɴ ꜱᴇᴛ ᴛᴏ {} ɪɴ ᴄʜᴀᴛ:{}".format(
                            amount, chat_name
                        )
                    )
                else:
                    message.reply_text(f"» ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ᴜᴘᴅᴀᴛᴇᴅ ᴀɴᴛɪ-ꜰʟᴏᴏᴅ ʟɪᴍɪᴛ ᴛᴏ {amount}!")
                return ""

        else:
            message.reply_text("» ɪɴᴠᴀʟɪᴅ ᴀʀɢᴜᴍᴇɴᴛ ᴘʟᴇᴀꜱᴇ ᴜꜱᴇ ᴀ ɴᴜᴍʙᴇʀ, 'ᴏꜰꜰ' ᴏʀ 'ɴᴏ'")
    else:
        message.reply_text(
            (
                "» ᴜꜱᴇ `/setflood <number>` ᴛᴏ ᴇɴᴀʙʟᴇ ᴀɴᴛɪ-ꜰʟᴏᴏᴅ.\nᴏʀ ᴜꜱᴇ `/setflood off` ᴛᴏ ᴅɪꜱᴀʙʟᴇ ᴀɴᴛɪꜰʟᴏᴏᴅ!."
            ),
            parse_mode="markdown",
        )
    return ""


@run_async
def flood(update, context):
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    msg = update.effective_message

    conn = connected(context.bot, update, chat, user.id, need_admin=False)
    if conn:
        chat_id = conn
        chat_name = dispatcher.bot.getChat(conn).title
    else:
        if update.effective_message.chat.type == "private":
            send_message(
                update.effective_message,
                "» ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ɪꜱ ᴍᴇᴀɴᴛ ᴛᴏ ᴜꜱᴇ ɪɴ ɢʀᴏᴜᴘ ɴᴏᴛ ɪɴ ᴘᴍ",
            )
            return
        chat_id = update.effective_chat.id
        chat_name = update.effective_message.chat.title

    limit = sql.get_flood_limit(chat_id)
    if limit == 0:
        if conn:
            msg.reply_text(
                "» ɪ'ᴍ ɴᴏᴛ ᴇɴꜰᴏʀᴄɪɴɢ ᴀɴʏ ꜰʟᴏᴏᴅ ᴄᴏɴᴛʀᴏʟ ɪɴ {}!".format(chat_name)
            )
        else:
            msg.reply_text("» ɪ'ᴍ ɴᴏᴛ ᴇɴꜰᴏʀᴄɪɴɢ ᴀɴʏ ꜰʟᴏᴏᴅ ᴄᴏɴᴛʀᴏʟ ʜᴇʀᴇ!")
    else:
        if conn:
            msg.reply_text(
                "» ɪ'ᴍ ᴄᴜʀʀᴇɴᴛʟʏ ʀᴇꜱᴛʀɪᴄᴛɪɴɢ ᴍᴇᴍʙᴇʀꜱ ᴀꜰᴛᴇʀ {} ᴄᴏɴꜱᴇᴄᴜᴛɪᴠᴇ ᴍᴇꜱꜱᴀɢᴇꜱ ɪɴ {}.".format(
                    limit, chat_name
                )
            )
        else:
            msg.reply_text(f"» ɪ'ᴍ ᴄᴜʀʀᴇɴᴛʟʏ ʀᴇꜱᴛʀɪᴄᴛɪɴɢ ᴍᴇᴍʙᴇʀꜱ ᴀꜰᴛᴇʀ {limit} ᴄᴏɴꜱᴇᴄᴜᴛɪᴠᴇ ᴍᴇꜱꜱᴀɢᴇꜱ.")


@run_async
@user_admin
def set_flood_mode(update, context):
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    msg = update.effective_message  # type: Optional[Message]
    args = context.args

    conn = connected(context.bot, update, chat, user.id, need_admin=True)
    if conn:
        chat = dispatcher.bot.getChat(conn)
        chat_id = conn
        chat_name = dispatcher.bot.getChat(conn).title
    else:
        if update.effective_message.chat.type == "private":
            send_message(
                update.effective_message,
                "» ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ɪꜱ ᴍᴇᴀɴᴛ ᴛᴏ ᴜꜱᴇ ɪɴ ɢʀᴏᴜᴘ ɴᴏᴛ ɪɴ ᴘᴍ!",
            )
            return ""
        chat = update.effective_chat
        chat_id = update.effective_chat.id
        chat_name = update.effective_message.chat.title

    if args:
        if args[0].lower() == "ban":
            settypeflood = "ʙᴀɴ"
            sql.set_flood_strength(chat_id, 1, "0")
        elif args[0].lower() == "kick":
            settypeflood = "ᴋɪᴄᴋ"
            sql.set_flood_strength(chat_id, 2, "0")
        elif args[0].lower() == "mute":
            settypeflood = "ᴍᴜᴛᴇ"
            sql.set_flood_strength(chat_id, 3, "0")
        elif args[0].lower() == "tban":
            if len(args) == 1:
                teks = """» ɪᴛ ʟᴏᴏᴋꜱ ʟɪᴋᴇ ʏᴏᴜ ᴛʀɪᴇᴅ ᴛᴏ ꜱᴇᴛ ᴛɪᴍᴇ ᴠᴀʟᴜᴇ ꜰᴏʀ ᴀɴᴛɪꜰʟᴏᴏᴅ ʙᴜᴛ ʏᴏᴜ ᴅɪᴅɴ'ᴛ ꜱᴘᴇᴄɪꜰɪᴇᴅ ᴛɪᴍᴇ; ᴛʀʏ, `/setfloodmode tban <timevalue>`.\n\n» ᴇxᴀᴍᴘʟᴇꜱ ᴏꜰ ᴛɪᴍᴇ ᴠᴀʟᴜᴇ: 4m = 4 minutes, 3h = 3 hours, 6d = 6 days, 5w = 5 weeks."""
                send_message(update.effective_message, teks, parse_mode="markdown")
                return
            settypeflood = "ᴛʙᴀɴ ꜰᴏʀ {}".format(args[1])
            sql.set_flood_strength(chat_id, 4, str(args[1]))
        elif args[0].lower() == "tmute":
            if len(args) == 1:
                teks = (
                    update.effective_message,
                    """» ɪᴛ ʟᴏᴏᴋꜱ ʟɪᴋᴇ ʏᴏᴜ ᴛʀɪᴇᴅ ᴛᴏ ꜱᴇᴛ ᴛɪᴍᴇ ᴠᴀʟᴜᴇ ꜰᴏʀ ᴀɴᴛɪꜰʟᴏᴏᴅ ʙᴜᴛ ʏᴏᴜ ᴅɪᴅɴ'ᴛ ꜱᴘᴇᴄɪꜰɪᴇᴅ ᴛɪᴍᴇ; ᴛʀʏ, `/setfloodmode tmute <timevalue>`.\n\n» ᴇxᴀᴍᴘʟᴇꜱ ᴏꜰ ᴛɪᴍᴇ ᴠᴀʟᴜᴇ: 4m = 4 minutes, 3h = 3 hours, 6d = 6 days, 5w = 5 weeks.""",
                )
                send_message(update.effective_message, teks, parse_mode="markdown")
                return
            settypeflood = "ᴛᴍᴜᴛᴇ ꜰᴏʀ {}".format(args[1])
            sql.set_flood_strength(chat_id, 5, str(args[1]))
        else:
            send_message(
                update.effective_message, "» ɪ ᴏɴʟʏ ᴜɴᴅᴇʀꜱᴛᴀɴᴅ `ʙᴀɴ/ᴋɪᴄᴋ/ᴍᴜᴛᴇ/ᴛʙᴀɴ/ᴛᴍᴜᴛᴇ`!"
            )
            return
        if conn:
            msg.reply_text(
                "» ᴇxᴄᴇᴇᴅɪɴɢ ᴄᴏɴꜱᴇᴄᴜᴛɪᴠᴇ ꜰʟᴏᴏᴅ ʟɪᴍɪᴛ ᴡɪʟʟ ʀᴇꜱᴜʟᴛ ɪɴ {} ɪɴ {}!".format(
                    settypeflood, chat_name
                )
            )
        else:
            msg.reply_text(f"» ᴇxᴄᴇᴇᴅɪɴɢ ᴄᴏɴꜱᴇᴄᴜᴛɪᴠᴇ ꜰʟᴏᴏᴅ ʟɪᴍɪᴛ ᴡɪʟʟ ʀᴇꜱᴜʟᴛ ɪɴ {settypeflood}!")
        return ""
    else:
        getmode, getvalue = sql.get_flood_setting(chat.id)
        if getmode == 1:
            settypeflood = "ʙᴀɴ"
        elif getmode == 2:
            settypeflood = "ᴋɪᴄᴋ"
        elif getmode == 3:
            settypeflood = "ᴍᴜᴛᴇ"
        elif getmode == 4:
            settypeflood = "ᴛʙᴀɴ ꜰᴏʀ {}".format(getvalue)
        elif getmode == 5:
            settypeflood = "ᴛᴍᴜᴛᴇ ꜰᴏʀ {}".format(getvalue)
        if conn:
            msg.reply_text(
                "» ꜱᴇɴᴅɪɴɢ ᴍᴏʀᴇ ᴍᴇꜱꜱᴀɢᴇꜱ ᴛʜᴀɴ ꜰʟᴏᴏᴅ ʟɪᴍɪᴛ ᴡɪʟʟ ʀᴇꜱᴜʟᴛ ɪɴ {} ɪɴ {}.".format(
                    settypeflood, chat_name
                )
            )
        else:
            msg.reply_text(
                "» ꜱᴇɴᴅɪɴɢ ᴍᴏʀᴇ ᴍᴇꜱꜱᴀɢᴇꜱ ᴛʜᴀɴ ꜰʟᴏᴏᴅ ʟɪᴍɪᴛ ᴡɪʟʟ ʀᴇꜱᴜʟᴛ ɪɴ {}.".format(
                    settypeflood
                )
            )
    return ""


def __migrate__(old_chat_id, new_chat_id):
    sql.migrate_chat(old_chat_id, new_chat_id)


def __chat_settings__(chat_id, user_id):
    limit = sql.get_flood_limit(chat_id)
    if limit == 0:
        return "» ɴᴏᴛ ᴇɴꜰᴏʀᴄɪɴɢ ᴛᴏ ꜰʟᴏᴏᴅ ᴄᴏɴᴛʀᴏʟ."
    else:
        return "» ᴀɴᴛɪꜰʟᴏᴏᴅ ʜᴀꜱ ʙᴇᴇɴ ꜱᴇᴛ ᴛᴏ `{}`.".format(limit)


__help__ = """
‣ Antiflood allows you to take action on users that send more than X messages in a row. Exceeding the set flood will result in restricting that user.
‣ This will mute users if they send more than X messages in a row, bots are ignored.

  ➲ /flood: ɢᴇᴛ ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ꜰʟᴏᴏᴅ ᴄᴏɴᴛʀᴏʟ ꜱᴇᴛᴛɪɴɢ

𝗔𝗱𝗺𝗶𝗻𝘀 𝗼𝗻𝗹𝘆:
  ➲ /setflood <int/'no'/'off'>: ᴇɴᴀʙʟᴇꜱ ᴏʀ ᴅɪꜱᴀʙʟᴇꜱ ꜰʟᴏᴏᴅ ᴄᴏɴᴛʀᴏʟ
     **Example:** `/setflood 13`
  ➲ /setfloodmode <ban/kick/mute/tban/tmute> <value>: ᴀᴄᴛɪᴏɴ ᴛᴏ ᴘᴇʀꜰᴏʀᴍ ᴡʜᴇɴ ᴜꜱᴇʀ ʜᴀᴠᴇ ᴇxᴄᴇᴇᴅᴇᴅ ꜰʟᴏᴏᴅ ʟɪᴍɪᴛ. ʙᴀɴ/ᴋɪᴄᴋ/ᴍᴜᴛᴇ/ᴛᴍᴜᴛᴇ/ᴛʙᴀɴ

𝗡𝗼𝘁𝗲:
 » ᴠᴀʟᴜᴇ ᴍᴜꜱᴛ ʙᴇ ꜰɪʟʟᴇᴅ ꜰᴏʀ ᴛʙᴀɴ ᴀɴᴅ ᴛᴍᴜᴛᴇ!!
  It can be:
   5m = 5 minutes
   4h = 4 hours
   3d = 3 days
   1w = 1 week
"""

__mod_name__ = "Aɴᴛɪ-Fʟᴏᴏᴅ"

FLOOD_BAN_HANDLER = MessageHandler(
    Filters.all & ~Filters.status_update & Filters.group, check_flood
)
SET_FLOOD_HANDLER = CommandHandler("setflood", set_flood, filters=Filters.group)
SET_FLOOD_MODE_HANDLER = CommandHandler(
    "setfloodmode", set_flood_mode, pass_args=True
)  # , filters=Filters.group)
FLOOD_QUERY_HANDLER = CallbackQueryHandler(flood_button, pattern=r"unmute_flooder")
FLOOD_HANDLER = CommandHandler("flood", flood, filters=Filters.group)

dispatcher.add_handler(FLOOD_BAN_HANDLER, FLOOD_GROUP)
dispatcher.add_handler(FLOOD_QUERY_HANDLER)
dispatcher.add_handler(SET_FLOOD_HANDLER)
dispatcher.add_handler(SET_FLOOD_MODE_HANDLER)
dispatcher.add_handler(FLOOD_HANDLER)

__handlers__ = [
    (FLOOD_BAN_HANDLER, FLOOD_GROUP),
    SET_FLOOD_HANDLER,
    FLOOD_HANDLER,
    SET_FLOOD_MODE_HANDLER,
]
