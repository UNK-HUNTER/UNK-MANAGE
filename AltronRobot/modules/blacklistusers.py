# Module to blacklist users and prevent them from using commands by @ItzExStar
import html

from telegram import ParseMode, Update
from telegram.ext import CallbackContext, CommandHandler, run_async
from telegram.utils.helpers import mention_html

import AltronRobot.modules.sql.blacklistusers_sql as sql
from AltronRobot import DEV_USERS, OWNER_ID, dispatcher
from AltronRobot.modules.helper_funcs.chat_status import dev_plus
from AltronRobot.modules.helper_funcs.extraction import (
    extract_user,
    extract_user_and_text,
)
from AltronRobot.modules.channel import gloggable

BLACKLISTWHITELIST = [OWNER_ID] + DEV_USERS


@run_async
@dev_plus
@gloggable
def bl_user(update: Update, context: CallbackContext) -> str:
    message = update.effective_message
    bot, args = context.bot, context.args
    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text("I doubt that's a user.")
        return ""

    if user_id == bot.id:
        message.reply_text("How am I supposed to do my work if I am ignoring myself?")
        return ""

    if user_id in BLACKLISTWHITELIST:
        message.reply_text("No!\nNoticing Disasters is my job.")
        return ""

    sql.blacklist_user(user_id, reason)
    message.reply_text("» ɪ ꜱʜᴀʟʟ ɪɢɴᴏʀᴇ ᴛʜᴇ ᴇxɪꜱᴛᴇɴᴄᴇ ᴏꜰ ᴛʜɪꜱ ᴜꜱᴇʀ!")
    return


@run_async
@dev_plus
@gloggable
def unbl_user(update: Update, context: CallbackContext) -> str:
    message = update.effective_message
    bot, args = context.bot, context.args
    user_id = extract_user(message, args)

    if not user_id:
        message.reply_text("I doubt that's a user.")
        return ""

    if user_id == bot.id:
        message.reply_text("I always notice myself.")
        return ""

    if sql.is_user_blacklisted(user_id):
        sql.unblacklist_user(user_id)
        message.reply_text("» ɴᴏᴛɪᴄᴇꜱ ᴜꜱᴇʀ")
        return
    else:
        message.reply_text("I am not ignoring them at all though!")
        return ""


@run_async
@dev_plus
def bl_users(update: Update, context: CallbackContext):
    users = []
    bot = context.bot
    for each_user in sql.BLACKLIST_USERS:
        user = bot.get_chat(each_user)
        reason = sql.get_reason(each_user)

        if reason:
            users.append(
                f"• {mention_html(user.id, html.escape(user.first_name))} :- {reason}"
            )
        else:
            users.append(f"• {mention_html(user.id, html.escape(user.first_name))}")

    message = "» <b>ʙʟᴀᴄᴋʟɪꜱᴛᴇᴅ ᴜꜱᴇʀꜱ</b>\n\n"
    if not users:
        message += "» ɴᴏɴᴇ ɪꜱ ʙᴇɪɴɢ ɪɢɴᴏʀᴇᴅ ᴀꜱ ᴏꜰ ʏᴇᴛ."
    else:
        message += "\n".join(users)

    update.effective_message.reply_text(message, parse_mode=ParseMode.HTML)


def __user_info__(user_id):
    is_blacklisted = sql.is_user_blacklisted(user_id)

    text = "» ʙʟᴀᴄᴋʟɪꜱᴛᴇᴅ: <b>{}</b>"
    if user_id in [777000, 1087968824]:
        return ""
    if user_id == dispatcher.bot.id:
        return ""
    if is_blacklisted:
        text = text.format("ʏᴇꜱ")
        reason = sql.get_reason(user_id)
        if reason:
            text += f"\n» ʀᴇᴀꜱᴏɴ: <code>{reason}</code>"
    else:
        text = text.format("ɴᴏ")

    return text


BL_HANDLER = CommandHandler("ignore", bl_user)
UNBL_HANDLER = CommandHandler("notice", unbl_user)
BLUSERS_HANDLER = CommandHandler("ignorelist", bl_users)

dispatcher.add_handler(BL_HANDLER)
dispatcher.add_handler(UNBL_HANDLER)
dispatcher.add_handler(BLUSERS_HANDLER)

__mod_name__ = "Bʟ-Uꜱᴇʀꜱ"
__help__ = """
𝗕𝗹𝗮𝗰𝗸𝗹𝗶𝘀𝘁 𝗨𝘀𝗲𝗿𝘀:
  ➲ /ignore : ʙʟᴀᴄᴋʟɪꜱᴛꜱ ᴀ ᴜꜱᴇʀ ꜰʀᴏᴍ ᴜꜱɪɴɢ ᴛʜᴇ ʙᴏᴛ ᴇɴᴛɪʀᴇʟʏ
  ➲ /notice : ʀᴇᴍᴏᴠᴇꜱ ᴜꜱᴇʀ ꜰʀᴏᴍ ʙʟᴀᴄᴋʟɪꜱᴛ
  ➲ /ignorelist : ʟɪꜱᴛꜱ ɪɢɴᴏʀᴇᴅ ᴜꜱᴇʀꜱ
"""

__handlers__ = [BL_HANDLER, UNBL_HANDLER, BLUSERS_HANDLER]
