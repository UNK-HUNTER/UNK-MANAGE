import html
import random
import re
import time
from contextlib import suppress
from functools import partial

from telegram import (
    ChatPermissions,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ParseMode,
    Update,
)
from telegram.error import BadRequest
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    Filters,
    MessageHandler,
    run_async,
)
from telegram.utils.helpers import escape_markdown, mention_html, mention_markdown

import AltronRobot
import AltronRobot.modules.sql.welcome_sql as sql
from AltronRobot import (
    DEMONS,
    DEV_USERS,
    DRAGONS,
    JOIN_LOGGER,
    LOGGER,
    OWNER_ID,
    TIGERS,
    WOLVES,
    dispatcher,
)
from AltronRobot.modules.helper_funcs.chat_status import (
    is_user_ban_protected,
    user_admin,
)
from AltronRobot.modules.helper_funcs.misc import build_keyboard, revert_buttons
from AltronRobot.modules.helper_funcs.msg_types import get_welcome_type
from AltronRobot.modules.helper_funcs.string_handling import (
    escape_invalid_curly_brackets,
    markdown_parser,
)
from AltronRobot.modules.channel import loggable
from AltronRobot.modules.sql.global_bans_sql import is_user_gbanned

VALID_WELCOME_FORMATTERS = [
    "first",
    "last",
    "fullname",
    "username",
    "id",
    "count",
    "chatname",
    "mention",
]

ENUM_FUNC_MAP = {
    sql.Types.TEXT.value: dispatcher.bot.send_message,
    sql.Types.BUTTON_TEXT.value: dispatcher.bot.send_message,
    sql.Types.STICKER.value: dispatcher.bot.send_sticker,
    sql.Types.DOCUMENT.value: dispatcher.bot.send_document,
    sql.Types.PHOTO.value: dispatcher.bot.send_photo,
    sql.Types.AUDIO.value: dispatcher.bot.send_audio,
    sql.Types.VOICE.value: dispatcher.bot.send_voice,
    sql.Types.VIDEO.value: dispatcher.bot.send_video,
}

VERIFIED_USER_WAITLIST = {}


# do not async
def send(update, message, keyboard, backup_message):
    chat = update.effective_chat
    cleanserv = sql.clean_service(chat.id)
    reply = update.message.message_id
    # Clean service welcome
    if cleanserv:
        try:
            dispatcher.bot.delete_message(chat.id, update.message.message_id)
        except BadRequest:
            pass
        reply = False
    try:
        msg = update.effective_message.reply_text(
            message,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=keyboard,
            reply_to_message_id=reply,
        )
    except BadRequest as excp:
        if excp.message == "Reply message not found":
            msg = update.effective_message.reply_text(
                message,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboard,
                quote=False,
            )
        elif excp.message == "Button_url_invalid":
            msg = update.effective_message.reply_text(
                markdown_parser(
                    backup_message + "\nNote: the current message has an invalid url in one of its buttons. Please update."
                ),
                parse_mode=ParseMode.MARKDOWN,
                reply_to_message_id=reply,
            )
        elif excp.message == "Unsupported url protocol":
            msg = update.effective_message.reply_text(
                markdown_parser(
                    backup_message + "\nNote: the current message has buttons which use url protocols that are unsupported by telegram. Please update."
                ),
                parse_mode=ParseMode.MARKDOWN,
                reply_to_message_id=reply,
            )
        elif excp.message == "Wrong url host":
            msg = update.effective_message.reply_text(
                markdown_parser(
                    backup_message + "\nNote: the current message has some bad urls. Please update."
                ),
                parse_mode=ParseMode.MARKDOWN,
                reply_to_message_id=reply,
            )
            LOGGER.warning(message)
            LOGGER.warning(keyboard)
            LOGGER.exception("Could not parse! got invalid url host errors")
        elif excp.message == "Have no rights to send a message":
            return
        else:
            msg = update.effective_message.reply_text(
                markdown_parser(
                    backup_message + "\nNote: An error occured when sending the custom message. Please update."
                ),
                parse_mode=ParseMode.MARKDOWN,
                reply_to_message_id=reply,
            )
            LOGGER.exception()
    return msg


@run_async
@loggable
def new_member(update: Update, context: CallbackContext):
    bot, job_queue = context.bot, context.job_queue
    chat = update.effective_chat
    user = update.effective_user
    msg = update.effective_message

    should_welc, cust_welcome, cust_content, welc_type = sql.get_welc_pref(chat.id)
    welc_mutes = sql.welcome_mutes(chat.id)
    human_checks = sql.get_human_checks(user.id, chat.id)

    new_members = update.effective_message.new_chat_members

    for new_mem in new_members:

        welcome_log = None
        res = None
        sent = None
        should_mute = True
        welcome_bool = True
        media_wel = False

        if should_welc:

            reply = update.message.message_id
            cleanserv = sql.clean_service(chat.id)
            # Clean service welcome
            if cleanserv:
                try:
                    dispatcher.bot.delete_message(chat.id, update.message.message_id)
                except BadRequest:
                    pass
                reply = False

            # Give the owner a special welcome
            if new_mem.id == OWNER_ID:
                update.effective_message.reply_text(
                    "Oh, Genos? Let's get this moving.", reply_to_message_id=reply
                )
                welcome_log = (
                    f"{html.escape(chat.title)}\n"
                    f"#USER_JOINED\n"
                    f"Bot Owner just joined the group"
                )
                continue

            # Welcome Devs
            elif new_mem.id in DEV_USERS:
                update.effective_message.reply_text(
                    "Be cool! A member of the Altron Association just joined.",
                    reply_to_message_id=reply,
                )
                welcome_log = (
                    f"{html.escape(chat.title)}\n"
                    f"#USER_JOINED\n"
                    f"Bot Dev just joined the group"
                )
                continue

            # Welcome Sudos
            elif new_mem.id in DRAGONS:
                update.effective_message.reply_text(
                    "Whoa! A Dragon disaster just joined! Stay Alert!",
                    reply_to_message_id=reply,
                )
                welcome_log = (
                    f"{html.escape(chat.title)}\n"
                    f"#USER_JOINED\n"
                    f"Bot Sudo just joined the group"
                )
                continue

            # Welcome Support
            elif new_mem.id in DEMONS:
                update.effective_message.reply_text(
                    "Huh! Someone with a Demon disaster level just joined!",
                    reply_to_message_id=reply,
                )
                welcome_log = (
                    f"{html.escape(chat.title)}\n"
                    f"#USER_JOINED\n"
                    f"Bot Support just joined the group"
                )
                continue

            # Welcome Whitelisted
            elif new_mem.id in TIGERS:
                update.effective_message.reply_text(
                    "Roar! A Tiger disaster just joined!", reply_to_message_id=reply
                )
                welcome_log = (
                    f"{html.escape(chat.title)}\n"
                    f"#USER_JOINED\n"
                    f"A whitelisted user joined the chat"
                )
                continue

            # Welcome Tigers
            elif new_mem.id in WOLVES:
                update.effective_message.reply_text(
                    "Awoo! A Wolf disaster just joined!", reply_to_message_id=reply
                )
                welcome_log = (
                    f"{html.escape(chat.title)}\n"
                    f"#USER_JOINED\n"
                    f"A whitelisted user joined the chat"
                )
                continue

            # Welcome yourself
            elif new_mem.id == bot.id:
                creator = None
                if not AltronRobot.ALLOW_CHATS:
                    with suppress(BadRequest):
                        update.effective_message.reply_text(
                            f"Groups are disabled for {bot.first_name}, I'm outta here."
                        )
                    bot.leave_chat(update.effective_chat.id)
                    return
                for x in bot.bot.get_chat_administrators(update.effective_chat.id):
                    if x.status == "creator":
                        creator = x.user
                        break
                if creator:
                    bot.send_message(
                        JOIN_LOGGER,
                        "#NEW_GROUP\n<b>ɢʀᴏᴜᴘ ɴᴀᴍᴇ:</b> {}\n<b>ɪᴅ:</b> <code>{}</code>\n<b>ᴄʀᴇᴀᴛᴏʀ:</b> <code>{}</code>".format(
                            html.escape(chat.title), chat.id, html.escape(creator)
                        ),
                        parse_mode=ParseMode.HTML,
                    )
                else:
                    bot.send_message(
                        JOIN_LOGGER,
                        "#NEW_GROUP\n<b>ɢʀᴏᴜᴘ ɴᴀᴍᴇ:</b> {}\n<b>ɪᴅ:</b> <code>{}</code>".format(
                            html.escape(chat.title), chat.id
                        ),
                        parse_mode=ParseMode.HTML,
                    )
                update.effective_message.reply_text(
                    "Watashi ga kita!", reply_to_message_id=reply
                )
                continue

            else:
                buttons = sql.get_welc_buttons(chat.id)
                keyb = build_keyboard(buttons)

                if welc_type not in (sql.Types.TEXT, sql.Types.BUTTON_TEXT):
                    media_wel = True

                first_name = (
                    new_mem.first_name or "PersonWithNoName"
                )  # edge case of empty name - occurs for some bugs.

                if cust_welcome:
                    if cust_welcome == sql.DEFAULT_WELCOME:
                        cust_welcome = random.choice(
                            sql.DEFAULT_WELCOME_MESSAGES
                        ).format(first=escape_markdown(first_name))

                    if new_mem.last_name:
                        fullname = escape_markdown(f"{first_name} {new_mem.last_name}")
                    else:
                        fullname = escape_markdown(first_name)
                    count = chat.get_members_count()
                    mention = mention_markdown(new_mem.id, escape_markdown(first_name))
                    if new_mem.username:
                        username = "@" + escape_markdown(new_mem.username)
                    else:
                        username = mention

                    valid_format = escape_invalid_curly_brackets(
                        cust_welcome, VALID_WELCOME_FORMATTERS
                    )
                    res = valid_format.format(
                        first=escape_markdown(first_name),
                        last=escape_markdown(new_mem.last_name or first_name),
                        fullname=escape_markdown(fullname),
                        username=username,
                        mention=mention,
                        count=count,
                        chatname=escape_markdown(chat.title),
                        id=new_mem.id,
                    )

                else:
                    res = random.choice(sql.DEFAULT_WELCOME_MESSAGES).format(
                        first=escape_markdown(first_name)
                    )
                    keyb = []

                backup_message = random.choice(sql.DEFAULT_WELCOME_MESSAGES).format(
                    first=escape_markdown(first_name)
                )
                keyboard = InlineKeyboardMarkup(keyb)

        else:
            welcome_bool = False
            res = None
            keyboard = None
            backup_message = None
            reply = None

        # User exceptions from welcomemutes
        if (
            is_user_ban_protected(chat, new_mem.id, chat.get_member(new_mem.id))
            or human_checks
        ):
            should_mute = False
        # Join welcome: soft mute
        if new_mem.is_bot:
            should_mute = False

        if user.id == new_mem.id:
            if should_mute:
                if welc_mutes == "soft":
                    bot.restrict_chat_member(
                        chat.id,
                        new_mem.id,
                        permissions=ChatPermissions(
                            can_send_messages=True,
                            can_send_media_messages=False,
                            can_send_other_messages=False,
                            can_invite_users=False,
                            can_pin_messages=False,
                            can_send_polls=False,
                            can_change_info=False,
                            can_add_web_page_previews=False,
                        ),
                        until_date=(int(time.time() + 24 * 60 * 60)),
                    )
                if welc_mutes == "strong":
                    welcome_bool = False
                    if not media_wel:
                        VERIFIED_USER_WAITLIST.update(
                            {
                                new_mem.id: {
                                    "should_welc": should_welc,
                                    "media_wel": False,
                                    "status": False,
                                    "update": update,
                                    "res": res,
                                    "keyboard": keyboard,
                                    "backup_message": backup_message,
                                }
                            }
                        )
                    else:
                        VERIFIED_USER_WAITLIST.update(
                            {
                                new_mem.id: {
                                    "should_welc": should_welc,
                                    "chat_id": chat.id,
                                    "status": False,
                                    "media_wel": True,
                                    "cust_content": cust_content,
                                    "welc_type": welc_type,
                                    "res": res,
                                    "keyboard": keyboard,
                                }
                            }
                        )
                    new_join_mem = f'<a href="tg://user?id={user.id}">{html.escape(new_mem.first_name)}</a>'
                    message = msg.reply_text(
                        f"» {new_join_mem}, ᴄʟɪᴄᴋ ᴛʜᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴛᴏ ᴘʀᴏᴠᴇ ʏᴏᴜ'ʀᴇ ʜᴜᴍᴀɴ.\nʏᴏᴜ ʜᴀᴠᴇ 120 ꜱᴇᴄᴏɴᴅꜱ.",
                        reply_markup=InlineKeyboardMarkup(
                            [
                                {
                                    InlineKeyboardButton(
                                        text="» ʏᴇꜱ, ɪ'ᴍ ʜᴜᴍᴀɴ.",
                                        callback_data=f"user_join_({new_mem.id})",
                                    )
                                }
                            ]
                        ),
                        parse_mode=ParseMode.HTML,
                        reply_to_message_id=reply,
                    )
                    bot.restrict_chat_member(
                        chat.id,
                        new_mem.id,
                        permissions=ChatPermissions(
                            can_send_messages=False,
                            can_invite_users=False,
                            can_pin_messages=False,
                            can_send_polls=False,
                            can_change_info=False,
                            can_send_media_messages=False,
                            can_send_other_messages=False,
                            can_add_web_page_previews=False,
                        ),
                    )
                    job_queue.run_once(
                        partial(check_not_bot, new_mem, chat.id, message.message_id),
                        120,
                        name="welcomemute",
                    )

        if welcome_bool:
            if media_wel:
                sent = ENUM_FUNC_MAP[welc_type](
                    chat.id,
                    cust_content,
                    caption=res,
                    reply_markup=keyboard,
                    reply_to_message_id=reply,
                    parse_mode="markdown",
                )
            else:
                sent = send(update, res, keyboard, backup_message)

            prev_welc = sql.get_clean_pref(chat.id)
            if prev_welc:
                try:
                    bot.delete_message(chat.id, prev_welc)
                except BadRequest:
                    pass

                if sent:
                    sql.set_clean_welcome(chat.id, sent.message_id)

        if welcome_log:
            return welcome_log

        return (
            f"{html.escape(chat.title)}\n"
            f"#USER_JOINED\n"
            f"<b>User</b>: {mention_html(user.id, user.first_name)}\n"
            f"<b>ID</b>: <code>{user.id}</code>"
        )

    return ""


def check_not_bot(member, chat_id, message_id, context):
    bot = context.bot
    member_dict = VERIFIED_USER_WAITLIST.pop(member.id)
    member_status = member_dict.get("status")
    if not member_status:
        try:
            bot.unban_chat_member(chat_id, member.id)
        except:
            pass

        try:
            bot.edit_message_text(
                "*kicks user*\nThey can always rejoin and try.",
                chat_id=chat_id,
                message_id=message_id,
            )
        except:
            pass


@run_async
def left_member(update: Update, context: CallbackContext):
    bot = context.bot
    chat = update.effective_chat
    user = update.effective_user
    should_goodbye, cust_goodbye, goodbye_type = sql.get_gdbye_pref(chat.id)

    if user.id == bot.id:
        return

    if should_goodbye:
        reply = update.message.message_id
        cleanserv = sql.clean_service(chat.id)
        # Clean service welcome
        if cleanserv:
            try:
                dispatcher.bot.delete_message(chat.id, update.message.message_id)
            except BadRequest:
                pass
            reply = False

        left_mem = update.effective_message.left_chat_member
        if left_mem:

            # Dont say goodbyes to gbanned users
            if is_user_gbanned(left_mem.id):
                return

            # Ignore bot being kicked
            if left_mem.id == bot.id:
                return

            # Give the owner a special goodbye
            if left_mem.id == OWNER_ID:
                update.effective_message.reply_text(
                    "Oi! Genos! He left..", reply_to_message_id=reply
                )
                return

            # Give the devs a special goodbye
            elif left_mem.id in DEV_USERS:
                update.effective_message.reply_text(
                    "See you later at the Altron's Association!",
                    reply_to_message_id=reply,
                )
                return

            # if media goodbye, use appropriate function for it
            if goodbye_type != sql.Types.TEXT and goodbye_type != sql.Types.BUTTON_TEXT:
                ENUM_FUNC_MAP[goodbye_type](chat.id, cust_goodbye)
                return

            first_name = (
                left_mem.first_name or "PersonWithNoName"
            )  # edge case of empty name - occurs for some bugs.
            if cust_goodbye:
                if cust_goodbye == sql.DEFAULT_GOODBYE:
                    cust_goodbye = random.choice(sql.DEFAULT_GOODBYE_MESSAGES).format(
                        first=escape_markdown(first_name)
                    )
                if left_mem.last_name:
                    fullname = escape_markdown(f"{first_name} {left_mem.last_name}")
                else:
                    fullname = escape_markdown(first_name)
                count = chat.get_members_count()
                mention = mention_markdown(left_mem.id, first_name)
                if left_mem.username:
                    username = "@" + escape_markdown(left_mem.username)
                else:
                    username = mention

                valid_format = escape_invalid_curly_brackets(
                    cust_goodbye, VALID_WELCOME_FORMATTERS
                )
                res = valid_format.format(
                    first=escape_markdown(first_name),
                    last=escape_markdown(left_mem.last_name or first_name),
                    fullname=escape_markdown(fullname),
                    username=username,
                    mention=mention,
                    count=count,
                    chatname=escape_markdown(chat.title),
                    id=left_mem.id,
                )
                buttons = sql.get_gdbye_buttons(chat.id)
                keyb = build_keyboard(buttons)

            else:
                res = random.choice(sql.DEFAULT_GOODBYE_MESSAGES).format(
                    first=first_name
                )
                keyb = []

            keyboard = InlineKeyboardMarkup(keyb)

            send(
                update,
                res,
                keyboard,
                random.choice(sql.DEFAULT_GOODBYE_MESSAGES).format(first=first_name),
            )


@run_async
@user_admin
def welcome(update: Update, context: CallbackContext):
    args = context.args
    chat = update.effective_chat
    # if no args, show current replies.
    if not args or args[0].lower() == "noformat":
        noformat = True
        pref, welcome_m, cust_content, welcome_type = sql.get_welc_pref(chat.id)
        update.effective_message.reply_text(
            f"» This chat has it's welcome setting set to: `{pref}`.\n"
            f"» *ᴛʜᴇ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇꜱꜱᴀɢᴇ (not filling the {{}}) ɪꜱ:*",
            parse_mode=ParseMode.MARKDOWN,
        )

        if welcome_type == sql.Types.BUTTON_TEXT or welcome_type == sql.Types.TEXT:
            buttons = sql.get_welc_buttons(chat.id)
            if noformat:
                welcome_m += revert_buttons(buttons)
                update.effective_message.reply_text(welcome_m)

            else:
                keyb = build_keyboard(buttons)
                keyboard = InlineKeyboardMarkup(keyb)

                send(update, welcome_m, keyboard, sql.DEFAULT_WELCOME)
        else:
            buttons = sql.get_welc_buttons(chat.id)
            if noformat:
                welcome_m += revert_buttons(buttons)
                ENUM_FUNC_MAP[welcome_type](chat.id, cust_content, caption=welcome_m)

            else:
                keyb = build_keyboard(buttons)
                keyboard = InlineKeyboardMarkup(keyb)
                ENUM_FUNC_MAP[welcome_type](
                    chat.id,
                    cust_content,
                    caption=welcome_m,
                    reply_markup=keyboard,
                    parse_mode=ParseMode.MARKDOWN,
                    disable_web_page_preview=True,
                )

    elif len(args) >= 1:
        if args[0].lower() in ("on", "yes"):
            sql.set_welc_preference(str(chat.id), True)
            update.effective_message.reply_text("Okay! I'll greet members when they join.")

        elif args[0].lower() in ("off", "no"):
            sql.set_welc_preference(str(chat.id), False)
            update.effective_message.reply_text("I'll go loaf around and not welcome anyone then.")

        else:
            update.effective_message.reply_text("I understand 'on/yes' or 'off/no' only!")


@run_async
@user_admin
def goodbye(update: Update, context: CallbackContext):
    args = context.args
    chat = update.effective_chat

    if not args or args[0] == "noformat":
        noformat = True
        pref, goodbye_m, goodbye_type = sql.get_gdbye_pref(chat.id)
        update.effective_message.reply_text(
            f"» ᴛʜɪꜱ ᴄʜᴀᴛ ʜᴀꜱ ɪᴛ'ꜱ ɢᴏᴏᴅʙʏᴇ ꜱᴇᴛᴛɪɴɢ ꜱᴇᴛ ᴛᴏ: `{pref}`.\n"
            f"» *ᴛʜᴇ ɢᴏᴏᴅʙʏᴇ  ᴍᴇꜱꜱᴀɢᴇ (not filling the {{}}) ɪꜱ:*",
            parse_mode=ParseMode.MARKDOWN,
        )

        if goodbye_type == sql.Types.BUTTON_TEXT:
            buttons = sql.get_gdbye_buttons(chat.id)
            if noformat:
                goodbye_m += revert_buttons(buttons)
                update.effective_message.reply_text(goodbye_m)

            else:
                keyb = build_keyboard(buttons)
                keyboard = InlineKeyboardMarkup(keyb)

                send(update, goodbye_m, keyboard, sql.DEFAULT_GOODBYE)

        else:
            if noformat:
                ENUM_FUNC_MAP[goodbye_type](chat.id, goodbye_m)

            else:
                ENUM_FUNC_MAP[goodbye_type](
                    chat.id, goodbye_m, parse_mode=ParseMode.MARKDOWN
                )

    elif len(args) >= 1:
        if args[0].lower() in ("on", "yes"):
            sql.set_gdbye_preference(str(chat.id), True)
            update.effective_message.reply_text("Ok!")

        elif args[0].lower() in ("off", "no"):
            sql.set_gdbye_preference(str(chat.id), False)
            update.effective_message.reply_text("Ok!")

        else:
            update.effective_message.reply_text("I understand 'on/yes' or 'off/no' only!")


@run_async
@user_admin
@loggable
def set_welcome(update: Update, context: CallbackContext) -> str:
    chat = update.effective_chat
    user = update.effective_user
    msg = update.effective_message

    text, data_type, content, buttons = get_welcome_type(msg)

    if data_type is None:
        msg.reply_text("You didn't specify what to reply with!")
        return ""

    sql.set_custom_welcome(chat.id, content, text, data_type, buttons)
    msg.reply_text("» ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ꜱᴇᴛ ᴄᴜꜱᴛᴏᴍ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇꜱꜱᴀɢᴇ!")

    return (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#SET_WELCOME\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"Set the welcome message."
    )


@run_async
@user_admin
@loggable
def reset_welcome(update: Update, context: CallbackContext) -> str:
    chat = update.effective_chat
    user = update.effective_user

    sql.set_custom_welcome(chat.id, None, sql.DEFAULT_WELCOME, sql.Types.TEXT)
    update.effective_message.reply_text("ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ʀᴇꜱᴇᴛ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇꜱꜱᴀɢᴇ ᴛᴏ ᴅᴇꜰᴀᴜʟᴛ!")

    return (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#RESET_WELCOME\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"Reset the welcome message to default."
    )


@run_async
@user_admin
@loggable
def set_goodbye(update: Update, context: CallbackContext) -> str:
    chat = update.effective_chat
    user = update.effective_user
    msg = update.effective_message
    text, data_type, content, buttons = get_welcome_type(msg)

    if data_type is None:
        msg.reply_text("You didn't specify what to reply with!")
        return ""

    sql.set_custom_gdbye(chat.id, content or text, data_type, buttons)
    msg.reply_text("ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ꜱᴇᴛ ᴄᴜꜱᴛᴏᴍ ɢᴏᴏᴅʙʏᴇ ᴍᴇꜱꜱᴀɢᴇ!")
    return (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#SET_GOODBYE\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"Set the goodbye message."
    )


@run_async
@user_admin
@loggable
def reset_goodbye(update: Update, context: CallbackContext) -> str:
    chat = update.effective_chat
    user = update.effective_user

    sql.set_custom_gdbye(chat.id, sql.DEFAULT_GOODBYE, sql.Types.TEXT)
    update.effective_message.reply_text("ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ʀᴇꜱᴇᴛ ɢᴏᴏᴅʙʏᴇ ᴍᴇꜱꜱᴀɢᴇ ᴛᴏ ᴅᴇꜰᴀᴜʟᴛ!")

    return (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#RESET_GOODBYE\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"Reset the goodbye message."
    )


@run_async
@user_admin
@loggable
def welcomemute(update: Update, context: CallbackContext) -> str:
    args = context.args
    chat = update.effective_chat
    user = update.effective_user
    msg = update.effective_message

    if len(args) >= 1:
        if args[0].lower() in ("off", "no"):
            sql.set_welcome_mutes(chat.id, False)
            msg.reply_text("» ɪ ᴡɪʟʟ ɴᴏ ʟᴏɴɢᴇʀ ᴍᴜᴛᴇ ᴘᴇᴏᴘʟᴇ ᴏɴ ᴊᴏɪɴɪɴɢ!")
            return (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"#WELCOME_MUTE\n"
                f"<b>• Admin:</b> {mention_html(user.id, user.first_name)}\n"
                f"Has toggled welcome mute to <b>OFF</b>."
            )
        elif args[0].lower() in ["soft"]:
            sql.set_welcome_mutes(chat.id, "soft")
            msg.reply_text("» ɪ ᴡɪʟʟ ʀᴇꜱᴛʀɪᴄᴛ ᴜꜱᴇʀꜱ' ᴘᴇʀᴍɪꜱꜱɪᴏɴ ᴛᴏ ꜱᴇɴᴅ ᴍᴇᴅɪᴀ ꜰᴏʀ 24 ʜᴏᴜʀꜱ.")
            return (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"#WELCOME_MUTE\n"
                f"<b>• Admin:</b> {mention_html(user.id, user.first_name)}\n"
                f"Has toggled welcome mute to <b>SOFT</b>."
            )
        elif args[0].lower() in ["strong"]:
            sql.set_welcome_mutes(chat.id, "strong")
            msg.reply_text(
                "» ɪ ᴡɪʟʟ ɴᴏᴡ ᴍᴜᴛᴇ ᴘᴇᴏᴘʟᴇ ᴡʜᴇɴ ᴛʜᴇʏ ᴊᴏɪɴ ᴜɴᴛɪʟ ᴛʜᴇʏ ᴘʀᴏᴠᴇ ᴛʜᴇʏ'ʀᴇ ɴᴏᴛ ᴀ ʙᴏᴛ.\nᴛʜᴇʏ ᴡɪʟʟ ʜᴀᴠᴇ 120 ꜱᴇᴄᴏɴᴅꜱ ʙᴇꜰᴏʀᴇ ᴛʜᴇʏ ɢᴇᴛ ᴋɪᴄᴋᴇᴅ."
            )
            return (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"#WELCOME_MUTE\n"
                f"<b>• Admin:</b> {mention_html(user.id, user.first_name)}\n"
                f"Has toggled welcome mute to <b>STRONG</b>."
            )
        else:
            msg.reply_text(
                "Please enter <code>off</code>/<code>no</code>/<code>soft</code>/<code>strong</code>!",
                parse_mode=ParseMode.HTML,
            )
            return ""
    else:
        curr_setting = sql.welcome_mutes(chat.id)
        reply = (
            f"» ɢɪᴠᴇ ᴍᴇ ᴀ ꜱᴇᴛᴛɪɴɢ!\n» ᴄʜᴏᴏꜱᴇ ᴏɴᴇ ᴏᴜᴛ ᴏꜰ: <code>off</code>/<code>no</code> ᴏʀ <code>soft</code> ᴏʀ <code>strong</code> ᴏɴʟʏ!\n» ᴄᴜʀʀᴇɴᴛ ꜱᴇᴛᴛɪɴɢ: <code>{curr_setting}</code>"
        )
        msg.reply_text(reply, parse_mode=ParseMode.HTML)
        return ""


@run_async
@user_admin
@loggable
def clean_welcome(update: Update, context: CallbackContext) -> str:
    args = context.args
    chat = update.effective_chat
    user = update.effective_user

    if not args:
        clean_pref = sql.get_clean_pref(chat.id)
        if clean_pref:
            update.effective_message.reply_text("» ɪ ꜱʜᴏᴜʟᴅ ʙᴇ ᴅᴇʟᴇᴛɪɴɢ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇꜱꜱᴀɢᴇꜱ ᴜᴘ ᴛᴏ ᴛᴡᴏ ᴅᴀʏꜱ ᴏʟᴅ.")
        else:
            update.effective_message.reply_text("» ɪ'ᴍ ᴄᴜʀʀᴇɴᴛʟʏ ɴᴏᴛ ᴅᴇʟᴇᴛɪɴɢ ᴏʟᴅ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇꜱꜱᴀɢᴇꜱ!")
        return ""

    if args[0].lower() in ("on", "yes"):
        sql.set_clean_welcome(str(chat.id), True)
        update.effective_message.reply_text("» ɪ'ʟʟ ᴛʀʏ ᴛᴏ ᴅᴇʟᴇᴛᴇ ᴏʟᴅ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇꜱꜱᴀɢᴇꜱ!")
        return (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#CLEAN_WELCOME\n"
            f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
            f"Has toggled clean welcomes to <code>ON</code>."
        )
    elif args[0].lower() in ("off", "no"):
        sql.set_clean_welcome(str(chat.id), False)
        update.effective_message.reply_text("» ɪ ᴡᴏɴ'ᴛ ᴅᴇʟᴇᴛᴇ ᴏʟᴅ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇꜱꜱᴀɢᴇꜱ.")
        return (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#CLEAN_WELCOME\n"
            f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
            f"Has toggled clean welcomes to <code>OFF</code>."
        )
    else:
        update.effective_message.reply_text("I understand 'on/yes' or 'off/no' only!")
        return ""


@run_async
@user_admin
def cleanservice(update: Update, context: CallbackContext) -> str:
    args = context.args
    chat = update.effective_chat
    if chat.type != chat.PRIVATE:
        if len(args) >= 1:
            var = args[0]
            if var in ("no", "off"):
                sql.set_clean_service(chat.id, False)
                update.effective_message.reply_text("» ᴡᴇʟᴄᴏᴍᴇ ᴄʟᴇᴀɴ ꜱᴇʀᴠɪᴄᴇ ɪꜱ : off")
            elif var in ("yes", "on"):
                sql.set_clean_service(chat.id, True)
                update.effective_message.reply_text("» ᴡᴇʟᴄᴏᴍᴇ ᴄʟᴇᴀɴ ꜱᴇʀᴠɪᴄᴇ ɪꜱ : on")
            else:
                update.effective_message.reply_text("» ɪɴᴠᴀʟɪᴅ ᴏᴘᴛɪᴏɴ", parse_mode=ParseMode.HTML)
        else:
            update.effective_message.reply_text(
                "Usage is <code>on</code>/<code>yes</code> or <code>off</code>/<code>no</code>",
                parse_mode=ParseMode.HTML,
            )
    else:
        curr = sql.clean_service(chat.id)
        if curr:
            update.effective_message.reply_text("» ᴡᴇʟᴄᴏᴍᴇ ᴄʟᴇᴀɴ ꜱᴇʀᴠɪᴄᴇ ɪꜱ : on")
        else:
            update.effective_message.reply_text("» ᴡᴇʟᴄᴏᴍᴇ ᴄʟᴇᴀɴ ꜱᴇʀᴠɪᴄᴇ ɪꜱ : off")


@run_async
def user_button(update: Update, context: CallbackContext):
    chat = update.effective_chat
    user = update.effective_user
    query = update.callback_query
    bot = context.bot
    match = re.match(r"user_join_\((.+?)\)", query.data)
    message = update.effective_message
    join_user = int(match.group(1))

    if join_user == user.id:
        sql.set_human_checks(user.id, chat.id)
        member_dict = VERIFIED_USER_WAITLIST.pop(user.id)
        member_dict["status"] = True
        VERIFIED_USER_WAITLIST.update({user.id: member_dict})
        query.answer(text="Yeet! You're a human, unmuted!")
        bot.restrict_chat_member(
            chat.id,
            user.id,
            permissions=ChatPermissions(
                can_send_messages=True,
                can_invite_users=True,
                can_pin_messages=True,
                can_send_polls=True,
                can_change_info=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
            ),
        )
        try:
            bot.deleteMessage(chat.id, message.message_id)
        except:
            pass
        if member_dict["should_welc"]:
            if member_dict["media_wel"]:
                sent = ENUM_FUNC_MAP[member_dict["welc_type"]](
                    member_dict["chat_id"],
                    member_dict["cust_content"],
                    caption=member_dict["res"],
                    reply_markup=member_dict["keyboard"],
                    parse_mode="markdown",
                )
            else:
                sent = send(
                    member_dict["update"],
                    member_dict["res"],
                    member_dict["keyboard"],
                    member_dict["backup_message"],
                )

            prev_welc = sql.get_clean_pref(chat.id)
            if prev_welc:
                try:
                    bot.delete_message(chat.id, prev_welc)
                except BadRequest:
                    pass

                if sent:
                    sql.set_clean_welcome(chat.id, sent.message_id)

    else:
        query.answer(text="You're not allowed to do this!")


WELC_HELP_TXT = (
    "‣ ʏᴏᴜʀ ɢʀᴏᴜᴘ'ꜱ ᴡᴇʟᴄᴏᴍᴇ/ɢᴏᴏᴅʙʏᴇ ᴍᴇꜱꜱᴀɢᴇꜱ ᴄᴀɴ ʙᴇ ᴘᴇʀꜱᴏɴᴀʟɪꜱᴇᴅ ɪɴ ᴍᴜʟᴛɪᴘʟᴇ ᴡᴀʏꜱ. ɪꜰ ʏᴏᴜ ᴡᴀɴᴛ ᴛʜᴇ ᴍᴇꜱꜱᴀɢᴇꜱ ᴛᴏ ʙᴇ ɪɴᴅɪᴠɪᴅᴜᴀʟʟʏ ɢᴇɴᴇʀᴀᴛᴇᴅ, ʟɪᴋᴇ ᴛʜᴇ ᴅᴇꜰᴀᴜʟᴛ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇꜱꜱᴀɢᴇ ɪꜱ, ʏᴏᴜ ᴄᴀɴ ᴜꜱᴇ *ᴛʜᴇꜱᴇ* ᴠᴀʀɪᴀʙʟᴇꜱ:\n\n"
    " • `{first}` : ᴛʜɪꜱ ʀᴇᴘʀᴇꜱᴇɴᴛꜱ ᴛʜᴇ ᴜꜱᴇʀ'ꜱ *ꜰɪʀꜱᴛ* ɴᴀᴍᴇ\n"
    " • `{last}` : ᴛʜɪꜱ ʀᴇᴘʀᴇꜱᴇɴᴛꜱ ᴛʜᴇ ᴜꜱᴇʀ'ꜱ *ʟᴀꜱᴛ* ɴᴀᴍᴇ. ᴅᴇꜰᴀᴜʟᴛꜱ ᴛᴏ *ꜰɪʀꜱᴛ ɴᴀᴍᴇ* ɪꜰ ᴜꜱᴇʀ ʜᴀꜱ ɴᴏ ʟᴀꜱᴛ ɴᴀᴍᴇ.\n"
    " • `{fullname}` : ᴛʜɪꜱ ʀᴇᴘʀᴇꜱᴇɴᴛꜱ ᴛʜᴇ ᴜꜱᴇʀ'ꜱ *ꜰᴜʟʟ* ɴᴀᴍᴇ. ᴅᴇꜰᴀᴜʟᴛꜱ ᴛᴏ *ꜰɪʀꜱᴛ ɴᴀᴍᴇ* ɪꜰ ᴜꜱᴇʀ ʜᴀꜱ ɴᴏ ʟᴀꜱᴛ ɴᴀᴍᴇ.\n"
    " • `{username}` : ᴛʜɪꜱ ʀᴇᴘʀᴇꜱᴇɴᴛꜱ ᴛʜᴇ ᴜꜱᴇʀ'ꜱ *ᴜꜱᴇʀɴᴀᴍᴇ*. ᴅᴇꜰᴀᴜʟᴛꜱ ᴛᴏ ᴀ *ᴍᴇɴᴛɪᴏɴ* ᴏꜰ ᴛʜᴇ ᴜꜱᴇʀ'ꜱ ꜰɪʀꜱᴛ ɴᴀᴍᴇ ɪꜰ ʜᴀꜱ ɴᴏ ᴜꜱᴇʀɴᴀᴍᴇ.\n"
    " • `{mention}` : ᴛʜɪꜱ ꜱɪᴍᴘʟʏ *ᴍᴇɴᴛɪᴏɴꜱ* ᴀ ᴜꜱᴇʀ - ᴛᴀɢɢɪɴɢ ᴛʜᴇᴍ ᴡɪᴛʜ ᴛʜᴇɪʀ ꜰɪʀꜱᴛ ɴᴀᴍᴇ.\n"
    " • `{id}` : ᴛʜɪꜱ ʀᴇᴘʀᴇꜱᴇɴᴛꜱ ᴛʜᴇ ᴜꜱᴇʀ'ꜱ *ɪᴅ*\n"
    " • `{count}` : ᴛʜɪꜱ ʀᴇᴘʀᴇꜱᴇɴᴛꜱ ᴛʜᴇ ᴜꜱᴇʀ'ꜱ *ᴍᴇᴍʙᴇʀ ɴᴜᴍʙᴇʀ*.\n"
    " • `{chatname}` : ᴛʜɪꜱ ʀᴇᴘʀᴇꜱᴇɴᴛꜱ ᴛʜᴇ *ᴄᴜʀʀᴇɴᴛ ᴄʜᴀᴛ ɴᴀᴍᴇ*.\n"
    "\n‣ ᴇᴀᴄʜ ᴠᴀʀɪᴀʙʟᴇ ᴍᴜꜱᴛ ʙᴇ ꜱᴜʀʀᴏᴜɴᴅᴇᴅ ʙʏ `{}` ᴛᴏ ʙᴇ ʀᴇᴘʟᴀᴄᴇᴅ.\n"
    "‣ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇꜱꜱᴀɢᴇꜱ ᴀʟꜱᴏ ꜱᴜᴘᴘᴏʀᴛ ᴍᴀʀᴋᴅᴏᴡɴ, ꜱᴏ ʏᴏᴜ ᴄᴀɴ ᴍᴀᴋᴇ ᴀɴʏ ᴇʟᴇᴍᴇɴᴛꜱ ʙᴏʟᴅ/ɪᴛᴀʟɪᴄ/ᴄᴏᴅᴇ/ʟɪɴᴋꜱ.\n\n"
    "‣ ʙᴜᴛᴛᴏɴꜱ ᴀʀᴇ ᴀʟꜱᴏ ꜱᴜᴘᴘᴏʀᴛᴇᴅ, ꜱᴏ ʏᴏᴜ ᴄᴀɴ ᴍᴀᴋᴇ ʏᴏᴜʀ ᴡᴇʟᴄᴏᴍᴇꜱ ʟᴏᴏᴋ ᴀᴡᴇꜱᴏᴍᴇ ᴡɪᴛʜ ꜱᴏᴍᴇ ɴɪᴄᴇ ɪɴᴛʀᴏ ʙᴜᴛᴛᴏɴꜱ.\n"
    f"‣ ᴛᴏ ᴄʀᴇᴀᴛᴇ ᴀ ʙᴜᴛᴛᴏɴ ʟɪɴᴋɪɴɢ ᴛᴏ ʏᴏᴜʀ ʀᴜʟᴇꜱ, ᴜꜱᴇ ᴛʜɪꜱ: `[Rules](buttonurl://t.me/{dispatcher.bot.username}?start=group_id)`.\n"
    "‣ ꜱɪᴍᴘʟʏ ʀᴇᴘʟᴀᴄᴇ `group_id` ᴡɪᴛʜ ʏᴏᴜʀ ɢʀᴏᴜᴘ'ꜱ ɪᴅ, ᴡʜɪᴄʜ ᴄᴀɴ ʙᴇ ᴏʙᴛᴀɪɴᴇᴅ ᴠɪᴀ /id, ᴀɴᴅ ʏᴏᴜ'ʀᴇ ɢᴏᴏᴅ ᴛᴏ ɢᴏ.\n\n"
    "*Note:* ɢʀᴏᴜᴘ ɪᴅꜱ ᴀʀᴇ ᴜꜱᴜᴀʟʟʏ ᴘʀᴇᴄᴇᴅᴇᴅ ʙʏ ᴀ `-` ꜱɪɢɴ; ᴛʜɪꜱ ɪꜱ ʀᴇQᴜɪʀᴇᴅ, ꜱᴏ ᴘʟᴇᴀꜱᴇ ᴅᴏɴ'ᴛ ʀᴇᴍᴏᴠᴇ ɪᴛ.\n\n"
    "‣ ʏᴏᴜ ᴄᴀɴ ᴇᴠᴇɴ ꜱᴇᴛ ɪᴍᴀɢᴇꜱ/ɢɪꜰꜱ/ᴠɪᴅᴇᴏꜱ/ᴠᴏɪᴄᴇ ᴍᴇꜱꜱᴀɢᴇꜱ ᴀꜱ ᴛʜᴇ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇꜱꜱᴀɢᴇ ʙʏ ʀᴇᴘʟʏɪɴɢ ᴛᴏ ᴛʜᴇ ᴅᴇꜱɪʀᴇᴅ ᴍᴇᴅɪᴀ, ᴀɴᴅ ᴄᴀʟʟɪɴɢ `/setwelcome`."
)

WELC_MUTE_HELP_TXT = (
    "‣ ʏᴏᴜ ᴄᴀɴ ɢᴇᴛ ᴛʜᴇ ʙᴏᴛ ᴛᴏ ᴍᴜᴛᴇ ɴᴇᴡ ᴘᴇᴏᴘʟᴇ ᴡʜᴏ ᴊᴏɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ ᴀɴᴅ ʜᴇɴᴄᴇ ᴘʀᴇᴠᴇɴᴛ ꜱᴘᴀᴍʙᴏᴛꜱ ꜰʀᴏᴍ ꜰʟᴏᴏᴅɪɴɢ ʏᴏᴜʀ ɢʀᴏᴜᴘ.\n\n"
    "*The following options are possible:*\n"
    "• /welcomemute soft : ʀᴇꜱᴛʀɪᴄᴛꜱ ɴᴇᴡ ᴍᴇᴍʙᴇʀꜱ ꜰʀᴏᴍ ꜱᴇɴᴅɪɴɢ ᴍᴇᴅɪᴀ ꜰᴏʀ 24 ʜᴏᴜʀꜱ.\n"
    "• /welcomemute strong : ᴍᴜᴛᴇꜱ ɴᴇᴡ ᴍᴇᴍʙᴇʀꜱ ᴛɪʟʟ ᴛʜᴇʏ ᴛᴀᴘ ᴏɴ ᴀ ʙᴜᴛᴛᴏɴ ᴛʜᴇʀᴇʙʏ ᴠᴇʀɪꜰʏɪɴɢ ᴛʜᴇʏ'ʀᴇ ʜᴜᴍᴀɴ.\n"
    "• /welcomemute off : ᴛᴜʀɴꜱ ᴏꜰꜰ ᴡᴇʟᴄᴏᴍᴇᴍᴜᴛᴇ.\n\n"
    "*Note:* ꜱᴛʀᴏɴɢ ᴍᴏᴅᴇ ᴋɪᴄᴋꜱ ᴀ ᴜꜱᴇʀ ꜰʀᴏᴍ ᴛʜᴇ ᴄʜᴀᴛ ɪꜰ ᴛʜᴇʏ ᴅᴏɴᴛ ᴠᴇʀɪꜰʏ ɪɴ 120 ꜱᴇᴄᴏɴᴅꜱ. ᴛʜᴇʏ ᴄᴀɴ ᴀʟᴡᴀʏꜱ ʀᴇᴊᴏɪɴ ᴛʜᴏᴜɢʜ"
)


@run_async
@user_admin
def welcome_help(update: Update, context: CallbackContext):
    update.effective_message.reply_text(WELC_HELP_TXT, parse_mode=ParseMode.MARKDOWN)


@run_async
@user_admin
def welcome_mute_help(update: Update, context: CallbackContext):
    update.effective_message.reply_text(
        WELC_MUTE_HELP_TXT, parse_mode=ParseMode.MARKDOWN
    )


# TODO: get welcome data from group butler snap
# def __import_data__(chat_id, data):
#     welcome = data.get('info', {}).get('rules')
#     welcome = welcome.replace('$username', '{username}')
#     welcome = welcome.replace('$name', '{fullname}')
#     welcome = welcome.replace('$id', '{id}')
#     welcome = welcome.replace('$title', '{chatname}')
#     welcome = welcome.replace('$surname', '{lastname}')
#     welcome = welcome.replace('$rules', '{rules}')
#     sql.set_custom_welcome(chat_id, welcome, sql.Types.TEXT)


def __migrate__(old_chat_id, new_chat_id):
    sql.migrate_chat(old_chat_id, new_chat_id)


def __chat_settings__(chat_id, user_id):
    welcome_pref = sql.get_welc_pref(chat_id)[0]
    goodbye_pref = sql.get_gdbye_pref(chat_id)[0]
    return (
        "» ᴛʜɪꜱ ᴄʜᴀᴛ ʜᴀꜱ ɪᴛ'ꜱ ᴡᴇʟᴄᴏᴍᴇ ᴘʀᴇꜰᴇʀᴇɴᴄᴇ ꜱᴇᴛ ᴛᴏ `{}`.\n"
        "» ɪᴛ'ꜱ ɢᴏᴏᴅʙʏᴇ ᴘʀᴇꜰᴇʀᴇɴᴄᴇ ɪꜱ `{}`.".format(welcome_pref, goodbye_pref)
    )


__help__ = """
𝗔𝗱𝗺𝗶𝗻𝘀 𝗼𝗻𝗹𝘆:
 ➲ /welcome <on/off> : ᴇɴᴀʙʟᴇ/ᴅɪꜱᴀʙʟᴇ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇꜱꜱᴀɢᴇꜱ.
 ➲ /welcome : ꜱʜᴏᴡꜱ ᴄᴜʀʀᴇɴᴛ ᴡᴇʟᴄᴏᴍᴇ ꜱᴇᴛᴛɪɴɢꜱ.
 ➲ /welcome noformat : ꜱʜᴏᴡꜱ ᴄᴜʀʀᴇɴᴛ ᴡᴇʟᴄᴏᴍᴇ ꜱᴇᴛᴛɪɴɢꜱ, ᴡɪᴛʜᴏᴜᴛ ᴛʜᴇ ꜰᴏʀᴍᴀᴛᴛɪɴɢ - ᴜꜱᴇꜰᴜʟ ᴛᴏ ʀᴇᴄʏᴄʟᴇ ʏᴏᴜʀ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇꜱꜱᴀɢᴇꜱ!
 ➲ /goodbye : ꜱᴀᴍᴇ ᴜꜱᴀɢᴇ ᴀɴᴅ ᴀʀɢꜱ ᴀꜱ `/welcome`.
 ➲ /setwelcome <sometext> : ꜱᴇᴛ ᴀ ᴄᴜꜱᴛᴏᴍ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇꜱꜱᴀɢᴇ. ɪꜰ ᴜꜱᴇᴅ ʀᴇᴘʟʏɪɴɢ ᴛᴏ ᴍᴇᴅɪᴀ, ᴜꜱᴇꜱ ᴛʜᴀᴛ ᴍᴇᴅɪᴀ.
 ➲ /setgoodbye <sometext> : ꜱᴇᴛ ᴀ ᴄᴜꜱᴛᴏᴍ ɢᴏᴏᴅʙʏᴇ ᴍᴇꜱꜱᴀɢᴇ. ɪꜰ ᴜꜱᴇᴅ ʀᴇᴘʟʏɪɴɢ ᴛᴏ ᴍᴇᴅɪᴀ, ᴜꜱᴇꜱ ᴛʜᴀᴛ ᴍᴇᴅɪᴀ.
 ➲ /resetwelcome : ʀᴇꜱᴇᴛ ᴛᴏ ᴛʜᴇ ᴅᴇꜰᴀᴜʟᴛ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇꜱꜱᴀɢᴇ.
 ➲ /resetgoodbye : ʀᴇꜱᴇᴛ ᴛᴏ ᴛʜᴇ ᴅᴇꜰᴀᴜʟᴛ ɢᴏᴏᴅʙʏᴇ ᴍᴇꜱꜱᴀɢᴇ.
 ➲ /cleanwelcome <on/off> : ᴏɴ ɴᴇᴡ ᴍᴇᴍʙᴇʀ, ᴛʀʏ ᴛᴏ ᴅᴇʟᴇᴛᴇ ᴛʜᴇ ᴘʀᴇᴠɪᴏᴜꜱ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇꜱꜱᴀɢᴇ ᴛᴏ ᴀᴠᴏɪᴅ ꜱᴘᴀᴍᴍɪɴɢ ᴛʜᴇ ᴄʜᴀᴛ.
 ➲ /welcomemutehelp : ɢɪᴠᴇꜱ ɪɴꜰᴏʀᴍᴀᴛɪᴏɴ ᴀʙᴏᴜᴛ ᴡᴇʟᴄᴏᴍᴇ ᴍᴜᴛᴇꜱ.
 ➲ /cleanservice <on/off> : ᴅᴇʟᴇᴛᴇꜱ ᴛᴇʟᴇɢʀᴀᴍꜱ ᴡᴇʟᴄᴏᴍᴇ/ʟᴇꜰᴛ ꜱᴇʀᴠɪᴄᴇ ᴍᴇꜱꜱᴀɢᴇꜱ.

 *Example:* ᴜꜱᴇʀ ᴊᴏɪɴᴇᴅ ᴄʜᴀᴛ, ᴜꜱᴇʀ ʟᴇꜰᴛ ᴄʜᴀᴛ.

𝗪𝗲𝗹𝗰𝗼𝗺𝗲 𝗺𝗮𝗿𝗸𝗱𝗼𝘄𝗻: 
 ➲ /welcomehelp : ᴠɪᴇᴡ ᴍᴏʀᴇ ꜰᴏʀᴍᴀᴛᴛɪɴɢ ɪɴꜰᴏʀᴍᴀᴛɪᴏɴ ꜰᴏʀ ᴄᴜꜱᴛᴏᴍ ᴡᴇʟᴄᴏᴍᴇ/ɢᴏᴏᴅʙʏᴇ ᴍᴇꜱꜱᴀɢᴇꜱ.
"""

NEW_MEM_HANDLER = MessageHandler(Filters.status_update.new_chat_members, new_member)
LEFT_MEM_HANDLER = MessageHandler(Filters.status_update.left_chat_member, left_member)
WELC_PREF_HANDLER = CommandHandler("welcome", welcome, filters=Filters.group)
GOODBYE_PREF_HANDLER = CommandHandler("goodbye", goodbye, filters=Filters.group)
SET_WELCOME = CommandHandler("setwelcome", set_welcome, filters=Filters.group)
SET_GOODBYE = CommandHandler("setgoodbye", set_goodbye, filters=Filters.group)
RESET_WELCOME = CommandHandler("resetwelcome", reset_welcome, filters=Filters.group)
RESET_GOODBYE = CommandHandler("resetgoodbye", reset_goodbye, filters=Filters.group)
WELCOMEMUTE_HANDLER = CommandHandler("welcomemute", welcomemute, filters=Filters.group)
CLEAN_SERVICE_HANDLER = CommandHandler(
    "cleanservice", cleanservice, filters=Filters.group
)
CLEAN_WELCOME = CommandHandler("cleanwelcome", clean_welcome, filters=Filters.group)
WELCOME_HELP = CommandHandler("welcomehelp", welcome_help)
WELCOME_MUTE_HELP = CommandHandler("welcomemutehelp", welcome_mute_help)
BUTTON_VERIFY_HANDLER = CallbackQueryHandler(user_button, pattern=r"user_join_")

dispatcher.add_handler(NEW_MEM_HANDLER)
dispatcher.add_handler(LEFT_MEM_HANDLER)
dispatcher.add_handler(WELC_PREF_HANDLER)
dispatcher.add_handler(GOODBYE_PREF_HANDLER)
dispatcher.add_handler(SET_WELCOME)
dispatcher.add_handler(SET_GOODBYE)
dispatcher.add_handler(RESET_WELCOME)
dispatcher.add_handler(RESET_GOODBYE)
dispatcher.add_handler(CLEAN_WELCOME)
dispatcher.add_handler(WELCOME_HELP)
dispatcher.add_handler(WELCOMEMUTE_HANDLER)
dispatcher.add_handler(CLEAN_SERVICE_HANDLER)
dispatcher.add_handler(BUTTON_VERIFY_HANDLER)
dispatcher.add_handler(WELCOME_MUTE_HELP)

__mod_name__ = "Wᴇʟᴄᴏᴍᴇ"
__command_list__ = []
__handlers__ = [
    NEW_MEM_HANDLER,
    LEFT_MEM_HANDLER,
    WELC_PREF_HANDLER,
    GOODBYE_PREF_HANDLER,
    SET_WELCOME,
    SET_GOODBYE,
    RESET_WELCOME,
    RESET_GOODBYE,
    CLEAN_WELCOME,
    WELCOME_HELP,
    WELCOMEMUTE_HANDLER,
    CLEAN_SERVICE_HANDLER,
    BUTTON_VERIFY_HANDLER,
    WELCOME_MUTE_HELP,
]
