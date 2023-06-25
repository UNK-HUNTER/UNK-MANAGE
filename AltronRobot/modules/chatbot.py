import json
import re
from time import sleep

import requests
from telegram import (
    CallbackQuery,
    Chat,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ParseMode,
    Update,
    User,
)
from telegram.error import BadRequest, RetryAfter, Unauthorized
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    Filters,
    MessageHandler,
    run_async,
)
from telegram.utils.helpers import mention_html

import AltronRobot.modules.sql.chatbot_sql as sql
from AltronRobot import dispatcher
from AltronRobot.modules.helper_funcs.chat_status import user_admin, user_admin_no_reply
from AltronRobot.modules.helper_funcs.filters import CustomFilters
from AltronRobot.modules.channel import gloggable


@run_async
@user_admin_no_reply
@gloggable
def altronrm(update: Update, context: CallbackContext) -> str:
    query: Optional[CallbackQuery] = update.callback_query
    user: Optional[User] = update.effective_user
    match = re.match(r"rm_chat\((.+?)\)", query.data)
    if match:
        user_id = match.group(1)
        chat: Optional[Chat] = update.effective_chat
        is_alt = sql.rem_alt(chat.id)
        if is_alt:
            is_alt = sql.rem_alt(user_id)
            return ""
        else:
            update.effective_message.edit_text(
                "{} ᴄʜᴀᴛʙᴏᴛ ᴅɪsᴀʙʟᴇᴅ ʙʏ {}.".format(
                    dispatcher.bot.first_name, mention_html(user.id, user.first_name)
                ),
                parse_mode=ParseMode.HTML,
            )

    return ""


@run_async
@user_admin_no_reply
@gloggable
def altronadd(update: Update, context: CallbackContext) -> str:
    query: Optional[CallbackQuery] = update.callback_query
    user: Optional[User] = update.effective_user
    match = re.match(r"add_chat\((.+?)\)", query.data)
    if match:
        user_id = match.group(1)
        chat: Optional[Chat] = update.effective_chat
        is_alt = sql.set_alt(chat.id)
        if is_alt:
            is_alt = sql.set_alt(user_id)
        else:
            update.effective_message.edit_text(
                "{} ᴄʜᴀᴛʙᴏᴛ ᴇɴᴀʙʟᴇᴅ ʙʏ {}.".format(
                    dispatcher.bot.first_name, mention_html(user.id, user.first_name)
                ),
                parse_mode=ParseMode.HTML,
            )

    return ""


@run_async
@user_admin
@gloggable
def itzaltron(update: Update, context: CallbackContext):
    update.effective_user
    message = update.effective_message
    msg = "» ᴄʜᴏᴏsᴇ ᴀɴ ᴏᴩᴛɪᴏɴ ᴛᴏ ᴇɴᴀʙʟᴇ/ᴅɪsᴀʙʟᴇ ᴄʜᴀᴛʙᴏᴛ"
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text="• ᴇɴᴀʙʟᴇ •", callback_data="add_chat({})"),
                InlineKeyboardButton(text="• ᴅɪsᴀʙʟᴇ •", callback_data="rm_chat({})"),
            ],
        ]
    )
    message.reply_text(
        msg,
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML,
    )


def alt_message(context: CallbackContext, message):
    reply_message = message.reply_to_message
    if message.text.lower() == "altron":
        return True
    if reply_message:
        if reply_message.from_user.id == context.bot.get_me().id:
            return True
    else:
        return False


def chatbot(update: Update, context: CallbackContext):
    message = update.effective_message
    chat_id = update.effective_chat.id
    is_alt = sql.is_alt(chat_id)
    if not is_alt:
        return

    if message.text and not message.document:
        if not alt_message(context, message):
            return
        evil = message.text
        url = f"http://api.roseloverx.com/api/chatbot?message={evil}"
        request = requests.get(url)
        results = json.loads(request.text)
        result = f"{results['responses']}"
        sleep(0.3)
        message.reply_text(result[2:-2])


def list_all_chats(update: Update, context: CallbackContext):
    chats = sql.get_all_alt_chats()
    text = "» <b>ᴄʜᴀᴛʙᴏᴛ ᴇɴᴀʙʟᴇᴅ ᴄʜᴀᴛꜱ:</b>\n\n"
    for chat in chats:
        try:
            x = context.bot.get_chat(int(*chat))
            name = x.title or x.first_name
            text += f"• <code>{name}</code>\n"
        except (BadRequest, Unauthorized):
            sql.rem_alt(*chat)
        except RetryAfter as e:
            sleep(e.retry_after)
    update.effective_message.reply_text(text, parse_mode="HTML")


__help__ = """
𝗔𝗱𝗺𝗶𝗻𝘀 𝗼𝗻𝗹𝘆:
  ➲ /chatbot : ꜱʜᴏᴡꜱ ᴄʜᴀᴛʙᴏᴛ ᴄᴏɴᴛʀᴏʟ ᴘᴀɴᴇʟ
"""

__mod_name__ = "Cʜᴀᴛʙᴏᴛ"


CHATBOTK_HANDLER = CommandHandler("chatbot", itzaltron)
ADD_CHAT_HANDLER = CallbackQueryHandler(altronadd, pattern=r"add_chat")
RM_CHAT_HANDLER = CallbackQueryHandler(altronrm, pattern=r"rm_chat")
CHATBOT_HANDLER = MessageHandler(
    Filters.text
    & (~Filters.regex(r"^#[^\s]+") & ~Filters.regex(r"^!") & ~Filters.regex(r"^\/")),
    chatbot,
)
LIST_ALL_CHATS_HANDLER = CommandHandler(
    "allchats",
    list_all_chats,
    filters=CustomFilters.dev_filter,
)

dispatcher.add_handler(ADD_CHAT_HANDLER)
dispatcher.add_handler(CHATBOTK_HANDLER)
dispatcher.add_handler(RM_CHAT_HANDLER)
dispatcher.add_handler(LIST_ALL_CHATS_HANDLER)
dispatcher.add_handler(CHATBOT_HANDLER)

__handlers__ = [
    ADD_CHAT_HANDLER,
    CHATBOTK_HANDLER,
    RM_CHAT_HANDLER,
    LIST_ALL_CHATS_HANDLER,
    CHATBOT_HANDLER,
]
