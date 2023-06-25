import html
from typing import Optional

from telegram import Bot, Chat, ChatPermissions, ParseMode, Update
from telegram.error import BadRequest
from telegram.ext import CallbackContext, CommandHandler, run_async
from telegram.utils.helpers import mention_html

from AltronRobot import LOGGER, TIGERS, dispatcher
from AltronRobot.modules.helper_funcs.chat_status import (
    bot_admin,
    can_restrict,
    connection_status,
    is_user_admin,
    user_admin,
)
from AltronRobot.modules.helper_funcs.extraction import (
    extract_user,
    extract_user_and_text,
)
from AltronRobot.modules.helper_funcs.string_handling import extract_time
from AltronRobot.modules.channel import loggable


def check_user(user_id: int, bot: Bot, chat: Chat) -> Optional[str]:
    if not user_id:
        reply = "You don't seem to be referring to a user or the ID specified is incorrect..."
        return reply

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "User not found":
            reply = "I can't seem to find this user"
            return reply
        else:
            raise

    if user_id == bot.id:
        reply = "I'm not gonna MUTE myself, How high are you?"
        return reply

    if is_user_admin(chat, user_id, member) or user_id in TIGERS:
        reply = "Can't. Find someone else to mute but not this one."
        return reply

    return None


@run_async
@connection_status
@bot_admin
@user_admin
@loggable
def mute(update: Update, context: CallbackContext) -> str:
    bot = context.bot
    args = context.args

    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message

    user_id, reason = extract_user_and_text(message, args)
    reply = check_user(user_id, bot, chat)

    if reply:
        message.reply_text(reply)
        return ""

    member = chat.get_member(user_id)

    reply = (
        f"<code>❕</code><b>ᴍᴜᴛᴇᴅ</b>\n"
        f" <b>•  ᴍᴜᴛᴇᴅ ʙʏ:</b> {mention_html(user.id, user.first_name)}\n"
        f" <b>•  ᴜsᴇʀ:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}"
    )
    if reason:
        reply += f"\n<code> </code><b>•  ʀᴇᴀsᴏɴ:</b>\n {html.escape(reason)}"

    if member.can_send_messages is None or member.can_send_messages:
        chat_permissions = ChatPermissions(can_send_messages=False)
        bot.restrict_chat_member(chat.id, user_id, chat_permissions)
        bot.sendMessage(chat.id, reply, parse_mode=ParseMode.HTML,)
        return ""

    else:
        message.reply_text("» ᴛʜɪꜱ ᴜꜱᴇʀ ɪꜱ ᴀʟʀᴇᴀᴅʏ ᴍᴜᴛᴇᴅ!")

    return ""


@run_async
@connection_status
@bot_admin
@user_admin
@loggable
def unmute(update: Update, context: CallbackContext) -> str:
    bot, args = context.bot, context.args
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message

    user_id = extract_user(message, args)
    if not user_id:
        message.reply_text(
            "You'll need to either give me a username to unmute, or reply to someone to be unmuted."
        )
        return ""

    member = chat.get_member(int(user_id))

    if member.status != "kicked" and member.status != "left":
        if (
            member.can_send_messages
            and member.can_send_media_messages
            and member.can_send_other_messages
            and member.can_add_web_page_previews
        ):
            message.reply_text("» ᴛʜɪꜱ ᴜꜱᴇʀ ᴀʟʀᴇᴀᴅʏ ʜᴀꜱ ᴛʜᴇ ʀɪɢʜᴛ ᴛᴏ ꜱᴘᴇᴀᴋ.")
        else:
            chat_permissions = ChatPermissions(
                can_send_messages=True,
                can_invite_users=True,
                can_pin_messages=True,
                can_send_polls=True,
                can_change_info=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
            )
            try:
                bot.restrict_chat_member(chat.id, int(user_id), chat_permissions)
            except BadRequest:
                pass
            reply = (
                f"<code>❕</code><b>ᴜɴᴍᴜᴛᴇᴅ</b>\n"
                f" <b>•  ᴜɴᴍᴜᴛᴇᴅ ʙʏ:</b> {mention_html(user.id, user.first_name)}\n"
                f" <b>•  ᴜsᴇʀ:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}"
            )
            bot.sendMessage(chat.id, reply, parse_mode=ParseMode.HTML,)
            return ""
    else:
        message.reply_text(
            "This user isn't even in the chat, unmuting them won't make them talk more than they "
            "already do!"
        )

    return ""


@run_async
@connection_status
@bot_admin
@can_restrict
@user_admin
@loggable
def temp_mute(update: Update, context: CallbackContext) -> str:
    bot, args = context.bot, context.args
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message

    user_id, reason = extract_user_and_text(message, args)
    reply = check_user(user_id, bot, chat)

    if reply:
        message.reply_text(reply)
        return ""

    member = chat.get_member(user_id)

    if not reason:
        message.reply_text("You haven't specified a time to mute this user for!")
        return ""

    split_reason = reason.split(None, 1)

    time_val = split_reason[0].lower()
    if len(split_reason) > 1:
        reason = split_reason[1]
    else:
        reason = ""

    mutetime = extract_time(message, time_val)

    if not mutetime:
        return ""
    
    reply = (
            f"<code>❕</code><b>ᴛᴇᴍᴘ ᴍᴜᴛᴇᴅ</b>\n"
            f" <b>•  ᴍᴜᴛᴇᴅ ʙʏ:</b> {mention_html(user.id, user.first_name)}\n"
            f" <b>•  ᴜsᴇʀ:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}\n"
            f" <b>•  ᴛɪᴍᴇ:</b> {time_val}"
        )
    if reason:
        reply += f"\n <b>•  ʀᴇᴀsᴏɴ:</b> \n{html.escape(reason)}"

    try:
        if member.can_send_messages is None or member.can_send_messages:
            chat_permissions = ChatPermissions(can_send_messages=False)
            bot.restrict_chat_member(
                chat.id, user_id, chat_permissions, until_date=mutetime
            )
            bot.sendMessage(chat.id, reply, parse_mode=ParseMode.HTML,)
            return ""
        else:
            message.reply_text("» ᴛʜɪꜱ ᴜꜱᴇʀ ɪꜱ ᴀʟʀᴇᴀᴅʏ ᴍᴜᴛᴇᴅ.")

    except BadRequest as excp:
        if excp.message == "Reply message not found":
            message.reply_text(f"» Muted for {time_val}!", quote=False)
            return ""
        else:
            LOGGER.warning(update)
            LOGGER.exception(
                "ERROR muting user %s in chat %s (%s) due to %s",
                user_id,
                chat.title,
                chat.id,
                excp.message,
            )
            message.reply_text("Well damn, I can't mute that user.")

    return ""


__help__ = """
𝗔𝗱𝗺𝗶𝗻𝘀 𝗼𝗻𝗹𝘆:
 ➲ /mute <userhandle>: ꜱɪʟᴇɴᴄᴇꜱ ᴀ ᴜꜱᴇʀ. ᴄᴀɴ ᴀʟꜱᴏ ʙᴇ ᴜꜱᴇᴅ ᴀꜱ ᴀ ʀᴇᴘʟʏ, ᴍᴜᴛɪɴɢ ᴛʜᴇ ʀᴇᴘʟɪᴇᴅ ᴛᴏ ᴜꜱᴇʀ.
 ➲ /tmute <userhandle> x(m/h/d): ᴍᴜᴛᴇꜱ ᴀ ᴜꜱᴇʀ ꜰᴏʀ x ᴛɪᴍᴇ. (ᴠɪᴀ ʜᴀɴᴅʟᴇ, ᴏʀ ʀᴇᴘʟʏ).
   `m` = `minutes`, `h` = `hours`, `d` = `days`.
 ➲ /unmute <userhandle>: ᴜɴᴍᴜᴛᴇꜱ ᴀ ᴜꜱᴇʀ. ᴄᴀɴ ᴀʟꜱᴏ ʙᴇ ᴜꜱᴇᴅ ᴀꜱ ᴀ ʀᴇᴘʟʏ, ᴍᴜᴛɪɴɢ ᴛʜᴇ ʀᴇᴘʟɪᴇᴅ ᴛᴏ ᴜꜱᴇʀ.
"""

MUTE_HANDLER = CommandHandler("mute", mute)
UNMUTE_HANDLER = CommandHandler("unmute", unmute)
TEMPMUTE_HANDLER = CommandHandler(["tmute", "tempmute"], temp_mute)

dispatcher.add_handler(MUTE_HANDLER)
dispatcher.add_handler(UNMUTE_HANDLER)
dispatcher.add_handler(TEMPMUTE_HANDLER)

__mod_name__ = "Mᴜᴛᴇ​"
__handlers__ = [MUTE_HANDLER, UNMUTE_HANDLER, TEMPMUTE_HANDLER]
