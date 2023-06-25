import html
import re

from telegram import ChatPermissions, ParseMode
from telegram.error import BadRequest
from telegram.ext import CommandHandler, Filters, MessageHandler, run_async

import AltronRobot.modules.sql.blacklist_sql as sql
from AltronRobot import LOGGER, dispatcher
from AltronRobot.modules.connection import connected
from AltronRobot.modules.disable import DisableAbleCommandHandler
from AltronRobot.modules.helper_funcs.alternate import send_message, typing_action
from AltronRobot.modules.helper_funcs.chat_status import user_admin, user_not_admin
from AltronRobot.modules.helper_funcs.extraction import extract_text
from AltronRobot.modules.helper_funcs.misc import split_message
from AltronRobot.modules.helper_funcs.string_handling import extract_time
from AltronRobot.modules.channel import loggable
from AltronRobot.modules.sql.approve_sql import is_approved
from AltronRobot.modules.warns import warn

BLACKLIST_GROUP = 11


@run_async
@user_admin
@typing_action
def blacklist(update, context):
    chat = update.effective_chat
    user = update.effective_user
    args = context.args

    conn = connected(context.bot, update, chat, user.id, need_admin=False)
    if conn:
        chat_id = conn
        chat_name = dispatcher.bot.getChat(conn).title
    else:
        if chat.type == "private":
            return
        chat_id = update.effective_chat.id
        chat_name = chat.title

    filter_list = "» ᴄᴜʀʀᴇɴᴛ ʙʟᴀᴄᴋʟɪꜱᴛᴇᴅ ᴡᴏʀᴅꜱ ɪɴ <b>{}</b>:\n\n".format(chat_name)

    all_blacklisted = sql.get_chat_blacklist(chat_id)

    if len(args) > 0 and args[0].lower() == "copy":
        for trigger in all_blacklisted:
            filter_list += "<code>{}</code>\n".format(html.escape(trigger))
    else:
        for trigger in all_blacklisted:
            filter_list += " - <code>{}</code>\n".format(html.escape(trigger))

    split_text = split_message(filter_list)
    for text in split_text:
        if filter_list == "» ᴄᴜʀʀᴇɴᴛ ʙʟᴀᴄᴋʟɪꜱᴛᴇᴅ ᴡᴏʀᴅꜱ ɪɴ <b>{}</b>:\n\n".format(
            html.escape(chat_name)
        ):
            send_message(
                update.effective_message,
                "» ɴᴏ ʙʟᴀᴄᴋʟɪꜱᴛᴇᴅ ᴡᴏʀᴅꜱ ɪɴ <b>{}</b>!".format(html.escape(chat_name)),
                parse_mode=ParseMode.HTML,
            )
            return
        send_message(update.effective_message, text, parse_mode=ParseMode.HTML)


@run_async
@user_admin
@typing_action
def add_blacklist(update, context):
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    words = msg.text.split(None, 1)

    conn = connected(context.bot, update, chat, user.id)
    if conn:
        chat_id = conn
        chat_name = dispatcher.bot.getChat(conn).title
    else:
        chat_id = update.effective_chat.id
        if chat.type == "private":
            return
        else:
            chat_name = chat.title

    if len(words) > 1:
        text = words[1]
        to_blacklist = list(
            {trigger.strip() for trigger in text.split("\n") if trigger.strip()}
        )
        for trigger in to_blacklist:
            sql.add_to_blacklist(chat_id, trigger.lower())

        if len(to_blacklist) == 1:
            send_message(
                update.effective_message,
                "» ᴀᴅᴅᴇᴅ ʙʟᴀᴄᴋʟɪꜱᴛ <code>{}</code> ɪɴ ᴄʜᴀᴛ: <b>{}</b>!".format(
                    html.escape(to_blacklist[0]), html.escape(chat_name)
                ),
                parse_mode=ParseMode.HTML,
            )

        else:
            send_message(
                update.effective_message,
                "» ᴀᴅᴅᴇᴅ ʙʟᴀᴄᴋʟɪꜱᴛ ᴛʀɪɢɢᴇʀ: <code>{}</code> ɪɴ <b>{}</b>!".format(
                    len(to_blacklist), html.escape(chat_name)
                ),
                parse_mode=ParseMode.HTML,
            )

    else:
        send_message(
            update.effective_message,
            "Tell me which words you would like to add in blacklist.",
        )


@run_async
@user_admin
@typing_action
def unblacklist(update, context):
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    words = msg.text.split(None, 1)

    conn = connected(context.bot, update, chat, user.id)
    if conn:
        chat_id = conn
        chat_name = dispatcher.bot.getChat(conn).title
    else:
        chat_id = update.effective_chat.id
        if chat.type == "private":
            return
        else:
            chat_name = chat.title

    if len(words) > 1:
        text = words[1]
        to_unblacklist = list(
            {trigger.strip() for trigger in text.split("\n") if trigger.strip()}
        )
        successful = 0
        for trigger in to_unblacklist:
            success = sql.rm_from_blacklist(chat_id, trigger.lower())
            if success:
                successful += 1

        if len(to_unblacklist) == 1:
            if successful:
                send_message(
                    update.effective_message,
                    "» ʀᴇᴍᴏᴠᴇᴅ <code>{}</code> ꜰʀᴏᴍ ʙʟᴀᴄᴋʟɪꜱᴛ ɪɴ <b>{}</b>!".format(
                        html.escape(to_unblacklist[0]), html.escape(chat_name)
                    ),
                    parse_mode=ParseMode.HTML,
                )
            else:
                send_message(
                    update.effective_message, "This is not a blacklist trigger!"
                )

        elif successful == len(to_unblacklist):
            send_message(
                update.effective_message,
                "» ʀᴇᴍᴏᴠᴇᴅ <code>{}</code> ꜰʀᴏᴍ ʙʟᴀᴄᴋʟɪꜱᴛ ɪɴ <b>{}</b>!".format(
                    successful, html.escape(chat_name)
                ),
                parse_mode=ParseMode.HTML,
            )

        elif not successful:
            send_message(
                update.effective_message,
                "None of these triggers exist so it can't be removed.",
                parse_mode=ParseMode.HTML,
            )

        else:
            send_message(
                update.effective_message,
                "» ʀᴇᴍᴏᴠᴇᴅ <code>{}</code> ꜰʀᴏᴍ ʙʟᴀᴄᴋʟɪꜱᴛ.\n» {} ᴅɪᴅ ɴᴏᴛ ᴇxɪꜱᴛ, ꜱᴏ ᴡᴇʀᴇ ɴᴏᴛ ʀᴇᴍᴏᴠᴇᴅ.".format(
                    successful, len(to_unblacklist) - successful
                ),
                parse_mode=ParseMode.HTML,
            )
    else:
        send_message(
            update.effective_message,
            "Tell me which words you would like to remove from blacklist!",
        )


@run_async
@loggable
@user_admin
@typing_action
def blacklist_mode(update, context):
    chat = update.effective_chat
    user = update.effective_user
    msg = update.effective_message
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
                "This command can be only used in group not in PM",
            )
            return ""
        chat = update.effective_chat
        chat_id = update.effective_chat.id
        chat_name = update.effective_message.chat.title

    if args:
        if args[0].lower() in ["off", "nothing", "no"]:
            settypeblacklist = "ᴅᴏ ɴᴏᴛʜɪɴɢ"
            sql.set_blacklist_strength(chat_id, 0, "0")
        elif args[0].lower() in ["del", "delete"]:
            settypeblacklist = "ᴅᴇʟᴇᴛᴇ ʙʟᴀᴄᴋʟɪꜱᴛᴇᴅ ᴍᴇꜱꜱᴀɢᴇ"
            sql.set_blacklist_strength(chat_id, 1, "0")
        elif args[0].lower() == "warn":
            settypeblacklist = "ᴡᴀʀɴ ᴛʜᴇ ꜱᴇɴᴅᴇʀ"
            sql.set_blacklist_strength(chat_id, 2, "0")
        elif args[0].lower() == "mute":
            settypeblacklist = "ᴍᴜᴛᴇ ᴛʜᴇ ꜱᴇɴᴅᴇʀ"
            sql.set_blacklist_strength(chat_id, 3, "0")
        elif args[0].lower() == "kick":
            settypeblacklist = "ᴋɪᴄᴋ ᴛʜᴇ ꜱᴇɴᴅᴇʀ"
            sql.set_blacklist_strength(chat_id, 4, "0")
        elif args[0].lower() == "ban":
            settypeblacklist = "ʙᴀɴ ᴛʜᴇ ꜱᴇɴᴅᴇʀ"
            sql.set_blacklist_strength(chat_id, 5, "0")
        elif args[0].lower() == "tban":
            if len(args) == 1:
                teks = """» ɪᴛ ʟᴏᴏᴋꜱ ʟɪᴋᴇ ʏᴏᴜ ᴛʀɪᴇᴅ ᴛᴏ ꜱᴇᴛ ᴛɪᴍᴇ ᴠᴀʟᴜᴇ ꜰᴏʀ ʙʟᴀᴄᴋʟɪꜱᴛ ʙᴜᴛ ʏᴏᴜ ᴅɪᴅɴ'ᴛ ꜱᴘᴇᴄɪꜰɪᴇᴅ ᴛɪᴍᴇ; ᴛʀʏ, `/blacklistmode tban <timevalue>`.\n\n» ᴇxᴀᴍᴘʟᴇꜱ ᴏꜰ ᴛɪᴍᴇ ᴠᴀʟᴜᴇ: 4m = 4 minutes, 3h = 3 hours, 6d = 6 days, 5w = 5 weeks."""
                send_message(update.effective_message, teks, parse_mode="markdown")
                return ""
            restime = extract_time(msg, args[1])
            if not restime:
                teks = """Invalid time value!\n\n
Example of time value: 4m = 4 minutes, 3h = 3 hours, 6d = 6 days, 5w = 5 weeks."""
                send_message(update.effective_message, teks, parse_mode="markdown")
                return ""
            settypeblacklist = "ᴛᴇᴍᴘᴏʀᴀʀɪʟʏ ʙᴀɴ ꜰᴏʀ {}".format(args[1])
            sql.set_blacklist_strength(chat_id, 6, str(args[1]))
        elif args[0].lower() == "tmute":
            if len(args) == 1:
                teks = """» ɪᴛ ʟᴏᴏᴋꜱ ʟɪᴋᴇ ʏᴏᴜ ᴛʀɪᴇᴅ ᴛᴏ ꜱᴇᴛ ᴛɪᴍᴇ ᴠᴀʟᴜᴇ ꜰᴏʀ ʙʟᴀᴄᴋʟɪꜱᴛ ʙᴜᴛ ʏᴏᴜ ᴅɪᴅɴ'ᴛ ꜱᴘᴇᴄɪꜰɪᴇᴅ ᴛɪᴍᴇ; ᴛʀʏ, `/blacklistmode tmute <timevalue>`.\n\n» ᴇxᴀᴍᴘʟᴇꜱ ᴏꜰ ᴛɪᴍᴇ ᴠᴀʟᴜᴇ: 4m = 4 minutes, 3h = 3 hours, 6d = 6 days, 5w = 5 weeks."""
                send_message(update.effective_message, teks, parse_mode="markdown")
                return ""
            restime = extract_time(msg, args[1])
            if not restime:
                teks = """Invalid time value!\n\n
Examples of time value: 4m = 4 minutes, 3h = 3 hours, 6d = 6 days, 5w = 5 weeks."""
                send_message(update.effective_message, teks, parse_mode="markdown")
                return ""
            settypeblacklist = "ᴛᴇᴍᴘᴏʀᴀʀɪʟʏ ᴍᴜᴛᴇ ꜰᴏʀ {}".format(args[1])
            sql.set_blacklist_strength(chat_id, 7, str(args[1]))
        else:
            send_message(
                update.effective_message,
                "I only understand: off/del/warn/ban/kick/mute/tban/tmute!",
            )
            return ""
        if conn:
            text = "» ᴄʜᴀɴɢᴇᴅ ʙʟᴀᴄᴋʟɪꜱᴛ ᴍᴏᴅᴇ: `{}` ɪɴ *{}*!".format(settypeblacklist, chat_name)
        else:
            text = "» ᴄʜᴀɴɢᴇᴅ ʙʟᴀᴄᴋʟɪꜱᴛ ᴍᴏᴅᴇ: `{}`!".format(settypeblacklist)
        send_message(update.effective_message, text, parse_mode="markdown")
        return
    else:
        getmode, getvalue = sql.get_blacklist_setting(chat.id)
        if getmode == 0:
            settypeblacklist = "ᴅᴏ ɴᴏᴛʜɪɴɢ"
        elif getmode == 1:
            settypeblacklist = "ᴅᴇʟᴇᴛᴇ"
        elif getmode == 2:
            settypeblacklist = "ᴡᴀʀɴ"
        elif getmode == 3:
            settypeblacklist = "ᴍᴜᴛᴇ"
        elif getmode == 4:
            settypeblacklist = "ᴋɪᴄᴋ"
        elif getmode == 5:
            settypeblacklist = "ʙᴀɴ"
        elif getmode == 6:
            settypeblacklist = "ᴛᴇᴍᴘᴏʀᴀʀɪʟʏ ʙᴀɴ ꜰᴏʀ {}".format(getvalue)
        elif getmode == 7:
            settypeblacklist = "ᴛᴇᴍᴘᴏʀᴀʀɪʟʏ ᴍᴜᴛᴇ ꜰᴏʀ {}".format(getvalue)
        if conn:
            text = "» ᴄᴜʀʀᴇɴᴛ ʙʟᴀᴄᴋʟɪꜱᴛᴍᴏᴅᴇ: *{}* ɪɴ *{}*.".format(settypeblacklist, chat_name)
        else:
            text = "» ᴄᴜʀʀᴇɴᴛ ʙʟᴀᴄᴋʟɪꜱᴛᴍᴏᴅᴇ: *{}*.".format(settypeblacklist)
        send_message(update.effective_message, text, parse_mode=ParseMode.MARKDOWN)
    return ""


def findall(p, s):
    i = s.find(p)
    while i != -1:
        yield i
        i = s.find(p, i + 1)


@run_async
@user_not_admin
def del_blacklist(update, context):
    chat = update.effective_chat
    message = update.effective_message
    user = update.effective_user
    bot = context.bot
    to_match = extract_text(message)
    if not to_match:
        return
    if is_approved(chat.id, user.id):
        return
    getmode, value = sql.get_blacklist_setting(chat.id)

    chat_filters = sql.get_chat_blacklist(chat.id)
    for trigger in chat_filters:
        pattern = r"( |^|[^\w])" + re.escape(trigger) + r"( |$|[^\w])"
        if re.search(pattern, to_match, flags=re.IGNORECASE):
            try:
                if getmode == 0:
                    return
                elif getmode == 1:
                    try:
                        message.delete()
                    except BadRequest:
                        pass
                elif getmode == 2:
                    try:
                        message.delete()
                    except BadRequest:
                        pass
                    warn(
                        update.effective_user,
                        chat,
                        ("» ᴜꜱɪɴɢ ʙʟᴀᴄᴋʟɪꜱᴛᴇᴅ ᴛʀɪɢɢᴇʀ: {}".format(trigger)),
                        message,
                        update.effective_user,
                    )
                    return
                elif getmode == 3:
                    message.delete()
                    bot.restrict_chat_member(
                        chat.id,
                        update.effective_user.id,
                        permissions=ChatPermissions(can_send_messages=False),
                    )
                    bot.sendMessage(
                        chat.id,
                        f"» ᴍᴜᴛᴇᴅ {user.first_name} ꜰᴏʀ ᴜꜱɪɴɢ ʙʟᴀᴄᴋʟɪꜱᴛᴇᴅ ᴡᴏʀᴅ: {trigger}!",
                    )
                    return
                elif getmode == 4:
                    message.delete()
                    res = chat.unban_member(update.effective_user.id)
                    if res:
                        bot.sendMessage(
                            chat.id,
                            f"» ᴋɪᴄᴋᴇᴅ {user.first_name} ꜰᴏʀ ᴜꜱɪɴɢ ʙʟᴀᴄᴋʟɪꜱᴛᴇᴅ ᴡᴏʀᴅ: {trigger}!",
                        )
                    return
                elif getmode == 5:
                    message.delete()
                    chat.kick_member(user.id)
                    bot.sendMessage(
                        chat.id,
                        f"» ʙᴀɴɴᴇᴅ {user.first_name} ꜰᴏʀ ᴜꜱɪɴɢ ʙʟᴀᴄᴋʟɪꜱᴛᴇᴅ ᴡᴏʀᴅ: {trigger}",
                    )
                    return
                elif getmode == 6:
                    message.delete()
                    bantime = extract_time(message, value)
                    chat.kick_member(user.id, until_date=bantime)
                    bot.sendMessage(
                        chat.id,
                        f"» ʙᴀɴɴᴇᴅ {user.first_name} ᴜɴᴛɪʟ '{value}' ꜰᴏʀ ᴜꜱɪɴɢ ʙʟᴀᴄᴋʟɪꜱᴛᴇᴅ ᴡᴏʀᴅ: {trigger}!",
                    )
                    return
                elif getmode == 7:
                    message.delete()
                    mutetime = extract_time(message, value)
                    bot.restrict_chat_member(
                        chat.id,
                        user.id,
                        until_date=mutetime,
                        permissions=ChatPermissions(can_send_messages=False),
                    )
                    bot.sendMessage(
                        chat.id,
                        f"» ᴍᴜᴛᴇᴅ {user.first_name} ᴜɴᴛɪʟ '{value}' ꜰᴏʀ ᴜꜱɪɴɢ ʙʟᴀᴄᴋʟɪꜱᴛᴇᴅ ᴡᴏʀᴅ: {trigger}!",
                    )
                    return
            except BadRequest as excp:
                if excp.message != "Message to delete not found":
                    LOGGER.exception("Error while deleting blacklist message.")
            break


def __import_data__(chat_id, data):
    # set chat blacklist
    blacklist = data.get("blacklist", {})
    for trigger in blacklist:
        sql.add_to_blacklist(chat_id, trigger)


def __migrate__(old_chat_id, new_chat_id):
    sql.migrate_chat(old_chat_id, new_chat_id)


def __chat_settings__(chat_id, user_id):
    blacklisted = sql.num_blacklist_chat_filters(chat_id)
    return "ᴛʜᴇʀᴇ ᴀʀᴇ {} ʙʟᴀᴄᴋʟɪꜱᴛᴇᴅ ᴡᴏʀᴅꜱ.".format(blacklisted)


def __stats__():
    return "• {} ʙʟᴀᴄᴋʟɪꜱᴛ ᴛʀɪɢɢᴇʀꜱ, ᴀᴄʀᴏꜱꜱ {} ᴄʜᴀᴛꜱ.".format(
        sql.num_blacklist_filters(), sql.num_blacklist_filter_chats()
    )


__mod_name__ = "Bʟ-Wᴏʀᴅꜱ"

__help__ = """
‣ ʙʟᴀᴄᴋʟɪꜱᴛꜱ ᴀʀᴇ ᴜꜱᴇᴅ ᴛᴏ ꜱᴛᴏᴘ ᴄᴇʀᴛᴀɪɴ ᴛʀɪɢɢᴇʀꜱ ꜰʀᴏᴍ ʙᴇɪɴɢ ꜱᴀɪᴅ ɪɴ ᴀ ɢʀᴏᴜᴘ. ᴀɴʏ ᴛɪᴍᴇ ᴛʜᴇ ᴛʀɪɢɢᴇʀ ɪꜱ ᴍᴇɴᴛɪᴏɴᴇᴅ, ᴛʜᴇ ᴍᴇꜱꜱᴀɢᴇ ᴡɪʟʟ ɪᴍᴍᴇᴅɪᴀᴛᴇʟʏ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ. ᴀ ɢᴏᴏᴅ ᴄᴏᴍʙᴏ ɪꜱ ꜱᴏᴍᴇᴛɪᴍᴇꜱ ᴛᴏ ᴘᴀɪʀ ᴛʜɪꜱ ᴜᴘ ᴡɪᴛʜ ᴡᴀʀɴ ꜰɪʟᴛᴇʀꜱ!

  ➲ /blacklist: ᴠɪᴇᴡ ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ʙʟᴀᴄᴋʟɪꜱᴛᴇᴅ ᴡᴏʀᴅꜱ.

𝗔𝗱𝗺𝗶𝗻𝘀 𝗼𝗻𝗹𝘆:
  ➲ /addblacklist <triggers>: ᴀᴅᴅ ᴀ ᴛʀɪɢɢᴇʀ ᴛᴏ ᴛʜᴇ ʙʟᴀᴄᴋʟɪꜱᴛ. ᴇᴀᴄʜ ʟɪɴᴇ ɪꜱ ᴄᴏɴꜱɪᴅᴇʀᴇᴅ ᴏɴᴇ ᴛʀɪɢɢᴇʀ, ꜱᴏ ᴜꜱɪɴɢ ᴅɪꜰꜰᴇʀᴇɴᴛ ʟɪɴᴇꜱ ᴡɪʟʟ ᴀʟʟᴏᴡ ʏᴏᴜ ᴛᴏ ᴀᴅᴅ ᴍᴜʟᴛɪᴘʟᴇ ᴛʀɪɢɢᴇʀꜱ.
  ➲ /unblacklist <triggers>: ʀᴇᴍᴏᴠᴇ ᴛʀɪɢɢᴇʀꜱ ꜰʀᴏᴍ ᴛʜᴇ ʙʟᴀᴄᴋʟɪꜱᴛ. ꜱᴀᴍᴇ ɴᴇᴡʟɪɴᴇ ʟᴏɢɪᴄ ᴀᴘᴘʟɪᴇꜱ ʜᴇʀᴇ, ꜱᴏ ʏᴏᴜ ᴄᴀɴ ʀᴇᴍᴏᴠᴇ ᴍᴜʟᴛɪᴘʟᴇ ᴛʀɪɢɢᴇʀꜱ ᴀᴛ ᴏɴᴄᴇ.
  ➲ /blacklistmode <off/del/warn/ban/kick/mute/tban/tmute>: ᴀᴄᴛɪᴏɴ ᴛᴏ ᴘᴇʀꜰᴏʀᴍ ᴡʜᴇɴ ꜱᴏᴍᴇᴏɴᴇ ꜱᴇɴᴅꜱ ʙʟᴀᴄᴋʟɪꜱᴛᴇᴅ ᴡᴏʀᴅꜱ.

⚠ 𝗡𝗼𝘁𝗲:
   » ʙʟᴀᴄᴋʟɪꜱᴛꜱ ᴅᴏ ɴᴏᴛ ᴀꜰꜰᴇᴄᴛ ɢʀᴏᴜᴘ ᴀᴅᴍɪɴꜱ.
"""

BLACKLIST_HANDLER = DisableAbleCommandHandler(
    "blacklist", blacklist, pass_args=True, admin_ok=True
)
ADD_BLACKLIST_HANDLER = CommandHandler("addblacklist", add_blacklist)
UNBLACKLIST_HANDLER = CommandHandler("unblacklist", unblacklist)
BLACKLISTMODE_HANDLER = CommandHandler("blacklistmode", blacklist_mode, pass_args=True)
BLACKLIST_DEL_HANDLER = MessageHandler(
    (Filters.text | Filters.command | Filters.sticker | Filters.photo) & Filters.group,
    del_blacklist,
    allow_edit=True,
)

dispatcher.add_handler(BLACKLIST_HANDLER)
dispatcher.add_handler(ADD_BLACKLIST_HANDLER)
dispatcher.add_handler(UNBLACKLIST_HANDLER)
dispatcher.add_handler(BLACKLISTMODE_HANDLER)
dispatcher.add_handler(BLACKLIST_DEL_HANDLER, group=BLACKLIST_GROUP)

__handlers__ = [
    BLACKLIST_HANDLER,
    ADD_BLACKLIST_HANDLER,
    UNBLACKLIST_HANDLER,
    BLACKLISTMODE_HANDLER,
    (BLACKLIST_DEL_HANDLER, BLACKLIST_GROUP),
]
