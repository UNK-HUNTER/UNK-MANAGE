import html
import re
from typing import Optional

import telegram
from telegram import (
    CallbackQuery,
    Chat,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    ParseMode,
    Update,
    User,
)
from telegram.error import BadRequest
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    DispatcherHandlerStop,
    Filters,
    MessageHandler,
    run_async,
)
from telegram.utils.helpers import mention_html

from AltronRobot import TIGERS, WOLVES, dispatcher
from AltronRobot.modules.disable import DisableAbleCommandHandler
from AltronRobot.modules.helper_funcs.chat_status import (
    bot_admin,
    can_restrict,
    is_user_admin,
    user_admin,
    user_admin_no_reply,
)
from AltronRobot.modules.helper_funcs.extraction import (
    extract_text,
    extract_user,
    extract_user_and_text,
)
from AltronRobot.modules.helper_funcs.filters import CustomFilters
from AltronRobot.modules.helper_funcs.misc import split_message
from AltronRobot.modules.helper_funcs.string_handling import split_quotes
from AltronRobot.modules.channel import loggable
from AltronRobot.modules.sql import warns_sql as sql
from AltronRobot.modules.sql.approve_sql import is_approved

WARN_HANDLER_GROUP = 9


# Not async
def warn(
    user: User,
    chat: Chat,
    reason: str,
    message: Message,
    warner: User = None,
) -> str:
    if is_user_admin(chat, user.id):
        return

    if user.id in TIGERS:
        if warner:
            message.reply_text("Tigers cant be warned.")
        else:
            message.reply_text(
                "Tiger triggered an auto warn filter!\n I can't warn tigers but they should avoid abusing this.",
            )
        return

    if user.id in WOLVES:
        if warner:
            message.reply_text("Wolf disasters are warn immune.")
        else:
            message.reply_text(
                "Wolf Disaster triggered an auto warn filter!\nI can't warn wolves but they should avoid abusing this.",
            )
        return

    limit, soft_warn = sql.get_warn_setting(chat.id)
    num_warns, reasons = sql.warn_user(user.id, chat.id, reason)
    if num_warns >= limit:
        sql.reset_warns(user.id, chat.id)
        if soft_warn:  # punch
            chat.unban_member(user.id)
            reply = (
                f"<code>❕</code><b>ᴘᴜɴᴄʜ ᴇᴠᴇɴᴛ</b>\n"
                f"<code> </code><b>•  ᴜꜱᴇʀ:</b> {mention_html(user.id, user.first_name)}\n"
                f"<code> </code><b>•  ᴄᴏᴜɴᴛ:</b> {limit}"
            )

        else:  # ban
            chat.kick_member(user.id)
            reply = (
                f"<code>❕</code><b>ʙᴀɴ ᴇᴠᴇɴᴛ</b>\n"
                f"<code> </code><b>•  ᴜꜱᴇʀ:</b> {mention_html(user.id, user.first_name)}\n"
                f"<code> </code><b>•  ᴄᴏᴜɴᴛ:</b> {limit}"
            )

        for warn_reason in reasons:
            reply += f"\n - {html.escape(warn_reason)}"

        keyboard = None

    else:
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "✨ ʀᴇᴍᴏᴠᴇ ✨",
                        callback_data="rm_warn({})".format(user.id),
                    ),
                ],
            ],
        )

        reply = (
            f"<code>❕</code><b>ᴡᴀʀɴ ᴇᴠᴇɴᴛ</b>\n"
            f"<code> </code><b>•  ᴜꜱᴇʀ:</b> {mention_html(user.id, user.first_name)}\n"
            f"<code> </code><b>•  ᴄᴏᴜɴᴛ:</b> {num_warns}/{limit}"
        )
        if reason:
            reply += f"\n<code> </code><b>•  ʀᴇᴀꜱᴏɴ:</b> {html.escape(reason)}"

    try:
        message.reply_text(reply, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    except BadRequest as excp:
        if excp.message == "Reply message not found":
            message.reply_text(reply, reply_markup=keyboard, parse_mode=ParseMode.HTML, quote=False,)
        else:
            raise
    return ""


@run_async
@user_admin_no_reply
@bot_admin
@loggable
def button(update: Update, context: CallbackContext) -> str:
    query: Optional[CallbackQuery] = update.callback_query
    user: Optional[User] = update.effective_user
    match = re.match(r"rm_warn\((.+?)\)", query.data)
    if match:
        user_id = match.group(1)
        chat: Optional[Chat] = update.effective_chat
        res = sql.remove_warn(user_id, chat.id)
        if res:
            update.effective_message.edit_text(
                "» ᴡᴀʀɴ ʀᴇᴍᴏᴠᴇᴅ ʙʏ {}.".format(mention_html(user.id, user.first_name)),
                parse_mode=ParseMode.HTML,
            )
            return ""
        else:
            update.effective_message.edit_text("User already has no warns.", parse_mode=ParseMode.HTML,)

    return ""


@run_async
@user_admin
@can_restrict
@loggable
def warn_user(update: Update, context: CallbackContext) -> str:
    args = context.args
    message: Optional[Message] = update.effective_message
    chat: Optional[Chat] = update.effective_chat
    warner: Optional[User] = update.effective_user

    user_id, reason = extract_user_and_text(message, args)
    if message.text.startswith("/d") and message.reply_to_message:
        message.reply_to_message.delete()
    if user_id:
        if (
            message.reply_to_message
            and message.reply_to_message.from_user.id == user_id
        ):
            return warn(
                message.reply_to_message.from_user,
                chat,
                reason,
                message.reply_to_message,
                warner,
            )
        else:
            return warn(chat.get_member(user_id).user, chat, reason, message, warner)
    else:
        message.reply_text("That looks like an invalid User ID to me.")
    return ""


@run_async
@user_admin
@bot_admin
@loggable
def reset_warns(update: Update, context: CallbackContext) -> str:
    args = context.args
    message: Optional[Message] = update.effective_message
    chat: Optional[Chat] = update.effective_chat
    user_id = extract_user(message, args)

    if user_id:
        sql.reset_warns(user_id, chat.id)
        message.reply_text("» ᴡᴀʀɴꜱ ʜᴀᴠᴇ ʙᴇᴇɴ ʀᴇꜱᴇᴛ!")
        return ""
    else:
        message.reply_text("No user has been designated!")
    return ""


@run_async
def warns(update: Update, context: CallbackContext):
    args = context.args
    message: Optional[Message] = update.effective_message
    chat: Optional[Chat] = update.effective_chat
    user_id = extract_user(message, args) or update.effective_user.id
    result = sql.get_warns(user_id, chat.id)

    if result and result[0] != 0:
        num_warns, reasons = result
        limit, soft_warn = sql.get_warn_setting(chat.id)

        if reasons:
            text = (f"» ᴛʜɪꜱ ᴜꜱᴇʀ ʜᴀꜱ {num_warns}/{limit} ᴡᴀʀɴꜱ, ꜰᴏʀ ᴛʜᴇ ꜰᴏʟʟᴏᴡɪɴɢ ʀᴇᴀꜱᴏɴꜱ:")
            for reason in reasons:
                text += f"\n • {reason}"

            msgs = split_message(text)
            for msg in msgs:
                update.effective_message.reply_text(msg)
        else:
            update.effective_message.reply_text(
                f"» ᴜꜱᴇʀ ʜᴀꜱ {num_warns}/{limit} ᴡᴀʀɴꜱ, ʙᴜᴛ ɴᴏ ʀᴇᴀꜱᴏɴꜱ ꜰᴏʀ ᴀɴʏ ᴏꜰ ᴛʜᴇᴍ.",
            )
    else:
        update.effective_message.reply_text("This user doesn't have any warns!")


# Dispatcher handler stop - do not async
@user_admin
def add_warn_filter(update: Update, context: CallbackContext):
    chat: Optional[Chat] = update.effective_chat
    msg: Optional[Message] = update.effective_message

    args = msg.text.split(None, 1)

    if len(args) < 2:
        return

    extracted = split_quotes(args[1])

    if len(extracted) >= 2:
        keyword = extracted[0].lower()
        content = extracted[1]

    else:
        return

    # Note: perhaps handlers can be removed somehow using sql.get_chat_filters
    for handler in dispatcher.handlers.get(WARN_HANDLER_GROUP, []):
        if handler.filters == (keyword, chat.id):
            dispatcher.remove_handler(handler, WARN_HANDLER_GROUP)

    sql.add_warn_filter(chat.id, keyword, content)

    update.effective_message.reply_text(f"» ᴡᴀʀɴ ʜᴀɴᴅʟᴇʀ ᴀᴅᴅᴇᴅ ꜰᴏʀ '{keyword}'!")
    raise DispatcherHandlerStop


@user_admin
def remove_warn_filter(update: Update, context: CallbackContext):
    chat: Optional[Chat] = update.effective_chat
    msg: Optional[Message] = update.effective_message

    args = msg.text.split(None, 1)

    if len(args) < 2:
        return

    extracted = split_quotes(args[1])

    if len(extracted) < 1:
        return

    to_remove = extracted[0]

    chat_filters = sql.get_chat_warn_triggers(chat.id)

    if not chat_filters:
        msg.reply_text("No warning filters are active here!")
        return

    for filt in chat_filters:
        if filt == to_remove:
            sql.remove_warn_filter(chat.id, to_remove)
            msg.reply_text("» ᴏᴋᴀʏ, ɪ'ʟʟ ꜱᴛᴏᴘ ᴡᴀʀɴɪɴɢ ᴘᴇᴏᴘʟᴇ ꜰᴏʀ ᴛʜᴀᴛ.")
            raise DispatcherHandlerStop

    msg.reply_text("» ᴛʜᴀᴛ'ꜱ ɴᴏᴛ ᴀ ᴄᴜʀʀᴇɴᴛ ᴡᴀʀɴɪɴɢ ꜰɪʟᴛᴇʀ - ʀᴜɴ /warnlist ꜰᴏʀ ᴀʟʟ ᴀᴄᴛɪᴠᴇ ᴡᴀʀɴɪɴɢ ꜰɪʟᴛᴇʀꜱ.")


@run_async
def list_warn_filters(update: Update, context: CallbackContext):
    chat: Optional[Chat] = update.effective_chat
    all_handlers = sql.get_chat_warn_triggers(chat.id)

    if not all_handlers:
        update.effective_message.reply_text("No warning filters are active here!")
        return

    filter_list = "<b>» ᴄᴜʀʀᴇɴᴛ ᴡᴀʀɴɪɴɢ ꜰɪʟᴛᴇʀꜱ ɪɴ ᴛʜɪꜱ ᴄʜᴀᴛ:</b>\n"
    for keyword in all_handlers:
        entry = f" - {html.escape(keyword)}\n"
        if len(entry) + len(filter_list) > telegram.MAX_MESSAGE_LENGTH:
            update.effective_message.reply_text(filter_list, parse_mode=ParseMode.HTML)
            filter_list = entry
        else:
            filter_list += entry

    if filter_list != "<b>» ᴄᴜʀʀᴇɴᴛ ᴡᴀʀɴɪɴɢ ꜰɪʟᴛᴇʀꜱ ɪɴ ᴛʜɪꜱ ᴄʜᴀᴛ:</b>\n":
        update.effective_message.reply_text(filter_list, parse_mode=ParseMode.HTML)


@run_async
@loggable
def reply_filter(update: Update, context: CallbackContext) -> str:
    chat: Optional[Chat] = update.effective_chat
    message: Optional[Message] = update.effective_message
    user: Optional[User] = update.effective_user

    if not user:
        return
    if user.id == 777000:
        return
    if is_approved(chat.id, user.id):
        return
    chat_warn_filters = sql.get_chat_warn_triggers(chat.id)
    to_match = extract_text(message)
    if not to_match:
        return ""

    for keyword in chat_warn_filters:
        pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
        if re.search(pattern, to_match, flags=re.IGNORECASE):
            user: Optional[User] = update.effective_user
            warn_filter = sql.get_warn_filter(chat.id, keyword)
            return warn(user, chat, warn_filter.reply, message)
    return ""


@run_async
@user_admin
@loggable
def set_warn_limit(update: Update, context: CallbackContext) -> str:
    args = context.args
    chat: Optional[Chat] = update.effective_chat
    user: Optional[User] = update.effective_user
    msg: Optional[Message] = update.effective_message

    if args:
        if args[0].isdigit():
            if int(args[0]) < 3:
                msg.reply_text("» ᴛʜᴇ ᴍɪɴɪᴍᴜᴍ ᴡᴀʀɴ ʟɪᴍɪᴛ ɪꜱ 3!")
            else:
                sql.set_warn_limit(chat.id, int(args[0]))
                msg.reply_text("» ᴜᴘᴅᴀᴛᴇᴅ ᴛʜᴇ ᴡᴀʀɴ ʟɪᴍɪᴛ ᴛᴏ {}".format(args[0]))
                return ""
        else:
            msg.reply_text("Give me a number as an arg!")
    else:
        limit, soft_warn = sql.get_warn_setting(chat.id)

        msg.reply_text("» ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ᴡᴀʀɴ ʟɪᴍɪᴛ ɪꜱ {}".format(limit))
    return ""


@run_async
@user_admin
def set_warn_strength(update: Update, context: CallbackContext):
    args = context.args
    chat: Optional[Chat] = update.effective_chat
    user: Optional[User] = update.effective_user
    msg: Optional[Message] = update.effective_message

    if args:
        if args[0].lower() in ("on", "yes"):
            sql.set_warn_strength(chat.id, False)
            msg.reply_text("» ᴛᴏᴏ ᴍᴀɴʏ ᴡᴀʀɴꜱ ᴡɪʟʟ ɴᴏᴡ ʀᴇꜱᴜʟᴛ ɪɴ ᴀ ʙᴀɴ!")
            return ""

        elif args[0].lower() in ("off", "no"):
            sql.set_warn_strength(chat.id, True)
            msg.reply_text(
                "» ᴛᴏᴏ ᴍᴀɴʏ ᴡᴀʀɴꜱ ᴡɪʟʟ ɴᴏᴡ ʀᴇꜱᴜʟᴛ ɪɴ ᴀ ɴᴏʀᴍᴀʟ ᴘᴜɴᴄʜ! ᴜꜱᴇʀꜱ ᴡɪʟʟ ʙᴇ ᴀʙʟᴇ ᴛᴏ ᴊᴏɪɴ ᴀɢᴀɪɴ ᴀꜰᴛᴇʀ.",
            )
            return ""

        else:
            msg.reply_text("I only understand on/yes/no/off!")
    else:
        limit, soft_warn = sql.get_warn_setting(chat.id)
        if soft_warn:
            msg.reply_text(
                "» ᴡᴀʀɴꜱ ᴀʀᴇ ᴄᴜʀʀᴇɴᴛʟʏ ꜱᴇᴛ ᴛᴏ *ᴘᴜɴᴄʜ* ᴜꜱᴇʀꜱ ᴡʜᴇɴ ᴛʜᴇʏ ᴇxᴄᴇᴇᴅ ᴛʜᴇ ʟɪᴍɪᴛꜱ.",
                parse_mode=ParseMode.MARKDOWN,
            )
        else:
            msg.reply_text(
                "» ᴡᴀʀɴꜱ ᴀʀᴇ ᴄᴜʀʀᴇɴᴛʟʏ ꜱᴇᴛ ᴛᴏ *ʙᴀɴ* ᴜꜱᴇʀꜱ ᴡʜᴇɴ ᴛʜᴇʏ ᴇxᴄᴇᴇᴅ ᴛʜᴇ ʟɪᴍɪᴛꜱ.",
                parse_mode=ParseMode.MARKDOWN,
            )
    return ""


def __stats__():
    return (
        f"• {sql.num_warns()} ᴏᴠᴇʀᴀʟʟ ᴡᴀʀɴꜱ, ᴀᴄʀᴏꜱꜱ {sql.num_warn_chats()} ᴄʜᴀᴛꜱ.\n"
        f"• {sql.num_warn_filters()} ᴡᴀʀɴ ꜰɪʟᴛᴇʀꜱ, ᴀᴄʀᴏꜱꜱ {sql.num_warn_filter_chats()} ᴄʜᴀᴛꜱ."
    )


def __import_data__(chat_id, data):
    for user_id, count in data.get("warns", {}).items():
        for x in range(int(count)):
            sql.warn_user(user_id, chat_id)


def __migrate__(old_chat_id, new_chat_id):
    sql.migrate_chat(old_chat_id, new_chat_id)


def __chat_settings__(chat_id, user_id):
    num_warn_filters = sql.num_warn_chat_filters(chat_id)
    limit, soft_warn = sql.get_warn_setting(chat_id)
    return (
        f"» ᴛʜɪꜱ ᴄʜᴀᴛ ʜᴀꜱ `{num_warn_filters}` ᴡᴀʀɴ ꜰɪʟᴛᴇʀꜱ.\n» ɪᴛ ᴛᴀᴋᴇꜱ `{limit}` ᴡᴀʀɴꜱ ʙᴇꜰᴏʀᴇ ᴛʜᴇ ᴜꜱᴇʀ ɢᴇᴛꜱ *{'ᴋɪᴄᴋᴇᴅ' if soft_warn else 'ʙᴀɴɴᴇᴅ'}*."
    )


__help__ = """
 ➲ /warns <userhandle> : ɢᴇᴛ ᴀ ᴜꜱᴇʀ'ꜱ ɴᴜᴍʙᴇʀ, ᴀɴᴅ ʀᴇᴀꜱᴏɴ, ᴏꜰ ᴡᴀʀɴꜱ.
 ➲ /warnlist : ʟɪꜱᴛ ᴏꜰ ᴀʟʟ ᴄᴜʀʀᴇɴᴛ ᴡᴀʀɴɪɴɢ ꜰɪʟᴛᴇʀꜱ.

𝗔𝗱𝗺𝗶𝗻𝘀 𝗼𝗻𝗹𝘆:
 ➲ /warn <userhandle> : ᴡᴀʀɴ ᴀ ᴜꜱᴇʀ. ᴀꜰᴛᴇʀ 3 ᴡᴀʀɴꜱ, ᴛʜᴇ ᴜꜱᴇʀ ᴡɪʟʟ ʙᴇ ʙᴀɴɴᴇᴅ ꜰʀᴏᴍ ᴛʜᴇ ɢʀᴏᴜᴘ. ᴄᴀɴ ᴀʟꜱᴏ ʙᴇ ᴜꜱᴇᴅ ᴀꜱ ᴀ ʀᴇᴘʟʏ.
 ➲ /dwarn <userhandle> : ᴡᴀʀɴ ᴀ ᴜꜱᴇʀ ᴀɴᴅ ᴅᴇʟᴇᴛᴇ ᴛʜᴇ ᴍᴇꜱꜱᴀɢᴇ. ᴀꜰᴛᴇʀ 3 ᴡᴀʀɴꜱ, ᴛʜᴇ ᴜꜱᴇʀ ᴡɪʟʟ ʙᴇ ʙᴀɴɴᴇᴅ ꜰʀᴏᴍ ᴛʜᴇ ɢʀᴏᴜᴘ. ᴄᴀɴ ᴀʟꜱᴏ ʙᴇ ᴜꜱᴇᴅ ᴀꜱ ᴀ ʀᴇᴘʟʏ.
 ➲ /resetwarn <userhandle> : ʀᴇꜱᴇᴛ ᴛʜᴇ ᴡᴀʀɴꜱ ꜰᴏʀ ᴀ ᴜꜱᴇʀ. ᴄᴀɴ ᴀʟꜱᴏ ʙᴇ ᴜꜱᴇᴅ ᴀꜱ ᴀ ʀᴇᴘʟʏ.
 ➲ /addwarn <keyword> <reply message> : ꜱᴇᴛ ᴀ ᴡᴀʀɴɪɴɢ ꜰɪʟᴛᴇʀ ᴏɴ ᴀ ᴄᴇʀᴛᴀɪɴ ᴋᴇʏᴡᴏʀᴅ. ɪꜰ ʏᴏᴜ ᴡᴀɴᴛ ʏᴏᴜʀ ᴋᴇʏᴡᴏʀᴅ ᴛᴏ ʙᴇ ᴀ ꜱᴇɴᴛᴇɴᴄᴇ, ᴇɴᴄᴏᴍᴘᴀꜱꜱ ɪᴛ ᴡɪᴛʜ Qᴜᴏᴛᴇꜱ, ᴀꜱ ꜱᴜᴄʜ: `/addwarn "very angry" This is an angry user`.
 ➲ /nowarn <keyword> : ꜱᴛᴏᴘ ᴀ ᴡᴀʀɴɪɴɢ ꜰɪʟᴛᴇʀ
 ➲ /warnlimit <num> : ꜱᴇᴛ ᴛʜᴇ ᴡᴀʀɴɪɴɢ ʟɪᴍɪᴛ
 ➲ /strongwarn <on/yes/off/no> : ɪꜰ ꜱᴇᴛ ᴛᴏ ᴏɴ, ᴇxᴄᴇᴇᴅɪɴɢ ᴛʜᴇ ᴡᴀʀɴ ʟɪᴍɪᴛ ᴡɪʟʟ ʀᴇꜱᴜʟᴛ ɪɴ ᴀ ʙᴀɴ. ᴇʟꜱᴇ, ᴡɪʟʟ ᴊᴜꜱᴛ ᴘᴜɴᴄʜ.
"""

__mod_name__ = "Wᴀʀɴs"

WARN_HANDLER = CommandHandler(["warn", "dwarn"], warn_user, filters=Filters.group)
RESET_WARN_HANDLER = CommandHandler(
    ["resetwarn", "resetwarns"],
    reset_warns,
    filters=Filters.group,
)
CALLBACK_QUERY_HANDLER = CallbackQueryHandler(button, pattern=r"rm_warn")
MYWARNS_HANDLER = DisableAbleCommandHandler("warns", warns, filters=Filters.group)
ADD_WARN_HANDLER = CommandHandler("addwarn", add_warn_filter, filters=Filters.group)
RM_WARN_HANDLER = CommandHandler(
    ["nowarn", "stopwarn"],
    remove_warn_filter,
    filters=Filters.group,
)
LIST_WARN_HANDLER = DisableAbleCommandHandler(
    ["warnlist", "warnfilters"],
    list_warn_filters,
    filters=Filters.group,
    admin_ok=True,
)
WARN_FILTER_HANDLER = MessageHandler(
    CustomFilters.has_text & Filters.group,
    reply_filter,
)
WARN_LIMIT_HANDLER = CommandHandler("warnlimit", set_warn_limit, filters=Filters.group)
WARN_STRENGTH_HANDLER = CommandHandler(
    "strongwarn",
    set_warn_strength,
    filters=Filters.group,
)

dispatcher.add_handler(WARN_HANDLER)
dispatcher.add_handler(CALLBACK_QUERY_HANDLER)
dispatcher.add_handler(RESET_WARN_HANDLER)
dispatcher.add_handler(MYWARNS_HANDLER)
dispatcher.add_handler(ADD_WARN_HANDLER)
dispatcher.add_handler(RM_WARN_HANDLER)
dispatcher.add_handler(LIST_WARN_HANDLER)
dispatcher.add_handler(WARN_LIMIT_HANDLER)
dispatcher.add_handler(WARN_STRENGTH_HANDLER)
dispatcher.add_handler(WARN_FILTER_HANDLER, WARN_HANDLER_GROUP)
