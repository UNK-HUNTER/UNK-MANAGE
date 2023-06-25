import html
import time
from datetime import datetime
from io import BytesIO

from telegram import ParseMode, Update
from telegram.error import BadRequest, TelegramError, Unauthorized
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    Filters,
    MessageHandler,
    run_async,
)
from telegram.utils.helpers import mention_html

import AltronRobot.modules.sql.global_bans_sql as sql
from AltronRobot import (
    DEMONS,
    DEV_USERS,
    DRAGONS,
    EVENT_LOGS,
    OWNER_ID,
    STRICT_GBAN,
    SUPPORT_CHAT,
    TIGERS,
    WOLVES,
    dispatcher,
)
from AltronRobot.modules.helper_funcs.chat_status import (
    is_user_admin,
    support_plus,
    user_admin,
)
from AltronRobot.modules.helper_funcs.extraction import (
    extract_user,
    extract_user_and_text,
)
from AltronRobot.modules.helper_funcs.misc import send_to_list
from AltronRobot.modules.sql.users_sql import get_user_com_chats

GBAN_ENFORCE_GROUP = 6

GBAN_ERRORS = {
    "User is an administrator of the chat",
    "Chat not found",
    "Not enough rights to restrict/unrestrict chat member",
    "User_not_participant",
    "Peer_id_invalid",
    "Group chat was deactivated",
    "Need to be inviter of a user to kick it from a basic group",
    "Chat_admin_required",
    "Only the creator of a basic group can kick group administrators",
    "Channel_private",
    "Not in the chat",
    "Can't remove chat owner",
}

UNGBAN_ERRORS = {
    "User is an administrator of the chat",
    "Chat not found",
    "Not enough rights to restrict/unrestrict chat member",
    "User_not_participant",
    "Method is available for supergroup and channel chats only",
    "Not in the chat",
    "Channel_private",
    "Chat_admin_required",
    "Peer_id_invalid",
    "User not found",
}


@run_async
@support_plus
def gban(update: Update, context: CallbackContext):
    bot, args = context.bot, context.args
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    log_message = ""

    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text(
            "You don't seem to be referring to a user or the ID specified is incorrect.."
        )
        return

    if int(user_id) in DEV_USERS:
        message.reply_text(
            "That user is part of the Association\nI can't act against our own."
        )
        return

    if int(user_id) in DRAGONS:
        message.reply_text(
            "I spy, with my little eye... a disaster! Why are you guys turning on each other?"
        )
        return

    if int(user_id) in DEMONS:
        message.reply_text(
            "OOOH someone's trying to gban a Demon Disaster! *grabs popcorn*"
        )
        return

    if int(user_id) in TIGERS:
        message.reply_text("That's a Tiger! They cannot be banned!")
        return

    if int(user_id) in WOLVES:
        message.reply_text("That's a Wolf! They cannot be banned!")
        return

    if user_id == bot.id:
        message.reply_text("You uhh...want me to punch myself?")
        return

    if user_id in [777000, 1087968824]:
        message.reply_text("Fool! You can't attack Telegram's native tech!")
        return

    try:
        user_chat = bot.get_chat(user_id)
    except BadRequest as excp:
        if excp.message == "User not found":
            message.reply_text("I can't seem to find this user.")
            return ""
        else:
            return

    if user_chat.type != "private":
        message.reply_text("That's not a user!")
        return

    if sql.is_user_gbanned(user_id):

        if not reason:
            message.reply_text(
                "This user is already gbanned; I'd change the reason, but you haven't given me one..."
            )
            return

        old_reason = sql.update_gban_reason(
            user_id, user_chat.username or user_chat.first_name, reason
        )
        if old_reason:
            message.reply_text(
                "This user is already gbanned, for the following reason:\n"
                "<code>{}</code>\n"
                "I've gone and updated it with your new reason!".format(
                    html.escape(old_reason)
                ),
                parse_mode=ParseMode.HTML,
            )

        else:
            message.reply_text(
                "This user is already gbanned, but had no reason set; I've gone and updated it!"
            )

        return

    message.reply_text(f"» ɢʙᴀɴɴɪɴɢ...")

    start_time = time.time()
    current_time = datetime.utcnow().strftime("%Y-%m-%d_%H:%M")

    if chat.type != "private":
        chat_origin = "‣ <b>{} ({})</b>\n".format(html.escape(chat.title), chat.id)
    else:
        chat_origin = "‣ <b>{}</b>\n".format(chat.id)

    log_message = (
        f"#GBANNED\n"
        f"‣ <b>ᴏʀɪɢɪɴᴀᴛᴇᴅ ꜰʀᴏᴍ:</b> <code>{chat_origin}</code>\n"
        f"‣ <b>ᴀᴅᴍɪɴ:</b> {mention_html(user.id, user.first_name)}\n"
        f"‣ <b>ʙᴀɴɴᴇᴅ ᴜꜱᴇʀ:</b> {mention_html(user_chat.id, user_chat.first_name)}\n"
        f"‣ <b>ʙᴀɴɴᴇᴅ ᴜꜱᴇʀ ɪᴅ:</b> <code>{user_chat.id}</code>\n"
        f"‣ <b>ᴇᴠᴇɴᴛ ꜱᴛᴀᴍᴘ:</b> <code>{current_time}</code>"
    )

    if reason:
        if chat.type == chat.SUPERGROUP and chat.username:
            log_message += f'\n‣ <b>ʀᴇᴀꜱᴏɴ:</b> <a href="https://telegram.me/{chat.username}/{message.message_id}">{reason}</a>'
        else:
            log_message += f"\n‣ <b>ʀᴇᴀꜱᴏɴ:</b> <code>{reason}</code>"

    if EVENT_LOGS:
        try:
            log = bot.send_message(EVENT_LOGS, log_message, parse_mode=ParseMode.HTML)
        except BadRequest:
            log = bot.send_message(
                EVENT_LOGS,
                log_message
                + "\n\n» ꜰᴏʀᴍᴀᴛᴛɪɴɢ ʜᴀꜱ ʙᴇᴇɴ ᴅɪꜱᴀʙʟᴇᴅ ᴅᴜᴇ ᴛᴏ ᴀɴ ᴜɴᴇxᴘᴇᴄᴛᴇᴅ ᴇʀʀᴏʀ.",
            )

    else:
        send_to_list(bot, DRAGONS + DEMONS, log_message, html=True)

    sql.gban_user(user_id, user_chat.username or user_chat.first_name, reason)

    chats = get_user_com_chats(user_id)
    gbanned_chats = 0

    for chat in chats:
        chat_id = int(chat)

        # Check if this group has disabled gbans
        if not sql.does_chat_gban(chat_id):
            continue

        try:
            bot.kick_chat_member(chat_id, user_id)
            gbanned_chats += 1

        except BadRequest as excp:
            if excp.message in GBAN_ERRORS:
                pass
            else:
                message.reply_text(f"Could not gban due to: {excp.message}")
                if EVENT_LOGS:
                    bot.send_message(
                        EVENT_LOGS,
                        f"Could not gban due to {excp.message}",
                        parse_mode=ParseMode.HTML,
                    )
                else:
                    send_to_list(
                        bot, DRAGONS + DEMONS, f"Could not gban due to: {excp.message}"
                    )
                sql.ungban_user(user_id)
                return
        except TelegramError:
            pass

    if EVENT_LOGS:
        log.edit_text(
            log_message + f"\n‣ <b>ᴄʜᴀᴛꜱ ᴀꜰꜰᴇᴄᴛᴇᴅ:</b> <code>{gbanned_chats}</code>",
            parse_mode=ParseMode.HTML,
        )
    else:
        send_to_list(
            bot,
            DRAGONS + DEMONS,
            f"» ɢʙᴀɴ ᴄᴏᴍᴘʟᴇᴛᴇ! (ᴜꜱᴇʀ ʙᴀɴɴᴇᴅ ɪɴ <code>{gbanned_chats}</code> ᴄʜᴀᴛꜱ)",
            html=True,
        )

    end_time = time.time()
    gban_time = round((end_time - start_time), 2)

    if gban_time > 60:
        gban_time = round((gban_time / 60), 2)
        message.reply_text("» ᴅᴏɴᴇ! ɢʙᴀɴɴᴇᴅ.", parse_mode=ParseMode.HTML)
    else:
        message.reply_text("» ᴅᴏɴᴇ! ɢʙᴀɴɴᴇᴅ.", parse_mode=ParseMode.HTML)

    try:
        bot.send_message(
            user_id,
            "#EVENT\n"
            "» ʏᴏᴜ ʜᴀᴠᴇ ʙᴇᴇɴ ᴍᴀʀᴋᴇᴅ ᴀꜱ ᴍᴀʟɪᴄɪᴏᴜꜱ ᴀɴᴅ ᴀꜱ ꜱᴜᴄʜ ʜᴀᴠᴇ ʙᴇᴇɴ ʙᴀɴɴᴇᴅ ꜰʀᴏᴍ ᴀɴʏ ꜰᴜᴛᴜʀᴇ ɢʀᴏᴜᴘꜱ ᴡᴇ ᴍᴀɴᴀɢᴇ."
            f"\n‣ <b>ʀᴇᴀꜱᴏɴ:</b> <code>{html.escape(user.reason)}</code>"
            f"‣ <b>ᴀᴘᴘᴇᴀʟ ᴄʜᴀᴛ:</b> @{SUPPORT_CHAT}",
            parse_mode=ParseMode.HTML,
        )
    except:
        pass  # bot probably blocked by user


@run_async
@support_plus
def ungban(update: Update, context: CallbackContext):
    bot, args = context.bot, context.args
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    log_message = ""

    user_id = extract_user(message, args)

    if not user_id:
        message.reply_text(
            "You don't seem to be referring to a user or the ID specified is incorrect.."
        )
        return

    user_chat = bot.get_chat(user_id)
    if user_chat.type != "private":
        message.reply_text("That's not a user!")
        return

    if not sql.is_user_gbanned(user_id):
        message.reply_text("ᴛʜɪꜱ ᴜꜱᴇʀ ɪꜱ ɴᴏᴛ ɢʙᴀɴɴᴇᴅ!")
        return

    message.reply_text(f"» ɪ'ʟʟ ɢɪᴠᴇ {user_chat.first_name} ᴀ ꜱᴇᴄᴏɴᴅ ᴄʜᴀɴᴄᴇ, ɢʟᴏʙᴀʟʟʏ.")

    start_time = time.time()
    current_time = datetime.utcnow().strftime("%Y-%m-%d_%H:%M")

    if chat.type != "private":
        chat_origin = f"‣ <b>{html.escape(chat.title)} ({chat.id})</b>\n"
    else:
        chat_origin = f"‣ <b>{chat.id}</b>\n"

    log_message = (
        f"#UNGBANNED\n"
        f"‣ <b>ᴏʀɪɢɪɴᴀᴛᴇᴅ ꜰʀᴏᴍ:</b> <code>{chat_origin}</code>\n"
        f"‣ <b>ᴀᴅᴍɪɴ:</b> {mention_html(user.id, user.first_name)}\n"
        f"‣ <b>ᴜɴʙᴀɴɴᴇᴅ ᴜꜱᴇʀ:</b> {mention_html(user_chat.id, user_chat.first_name)}\n"
        f"‣ <b>ᴜɴʙᴀɴɴᴇᴅ ᴜꜱᴇʀ ɪᴅ:</b> <code>{user_chat.id}</code>\n"
        f"‣ <b>ᴇᴠᴇɴᴛ ꜱᴛᴀᴍᴘ:</b> <code>{current_time}</code>"
    )

    if EVENT_LOGS:
        try:
            log = bot.send_message(EVENT_LOGS, log_message, parse_mode=ParseMode.HTML)
        except BadRequest:
            log = bot.send_message(
                EVENT_LOGS,
                log_message
                + "\n\n» ꜰᴏʀᴍᴀᴛᴛɪɴɢ ʜᴀꜱ ʙᴇᴇɴ ᴅɪꜱᴀʙʟᴇᴅ ᴅᴜᴇ ᴛᴏ ᴀɴ ᴜɴᴇxᴘᴇᴄᴛᴇᴅ ᴇʀʀᴏʀ.",
            )
    else:
        send_to_list(bot, DRAGONS + DEMONS, log_message, html=True)

    chats = get_user_com_chats(user_id)
    ungbanned_chats = 0

    for chat in chats:
        chat_id = int(chat)

        # Check if this group has disabled gbans
        if not sql.does_chat_gban(chat_id):
            continue

        try:
            member = bot.get_chat_member(chat_id, user_id)
            if member.status == "kicked":
                bot.unban_chat_member(chat_id, user_id)
                ungbanned_chats += 1

        except BadRequest as excp:
            if excp.message in UNGBAN_ERRORS:
                pass
            else:
                message.reply_text(f"Could not un-gban due to: {excp.message}")
                if EVENT_LOGS:
                    bot.send_message(
                        EVENT_LOGS,
                        f"Could not un-gban due to: {excp.message}",
                        parse_mode=ParseMode.HTML,
                    )
                else:
                    bot.send_message(
                        OWNER_ID, f"Could not un-gban due to: {excp.message}"
                    )
                return
        except TelegramError:
            pass

    sql.ungban_user(user_id)

    if EVENT_LOGS:
        log.edit_text(
            log_message + f"‣ \n<b>ᴄʜᴀᴛꜱ ᴀꜰꜰᴇᴄᴛᴇᴅ:</b> {ungbanned_chats}",
            parse_mode=ParseMode.HTML,
        )
    else:
        send_to_list(bot, DRAGONS + DEMONS, "» ᴜɴ-ɢʙᴀɴ ᴄᴏᴍᴘʟᴇᴛᴇ!")

    end_time = time.time()
    ungban_time = round((end_time - start_time), 2)

    if ungban_time > 60:
        ungban_time = round((ungban_time / 60), 2)
        message.reply_text(f"» ᴘᴇʀꜱᴏɴ ʜᴀꜱ ʙᴇᴇɴ ᴜɴ-ɢʙᴀɴɴᴇᴅ. ᴛᴏᴏᴋ {ungban_time} ᴍɪɴ")
    else:
        message.reply_text(f"» ᴘᴇʀꜱᴏɴ ʜᴀꜱ ʙᴇᴇɴ ᴜɴ-ɢʙᴀɴɴᴇᴅ. ᴛᴏᴏᴋ {ungban_time} ꜱᴇᴄ")


@run_async
@support_plus
def gbanlist(update: Update, context: CallbackContext):
    banned_users = sql.get_gban_list()

    if not banned_users:
        update.effective_message.reply_text(
            "» ᴛʜᴇʀᴇ ᴀʀᴇɴ'ᴛ ᴀɴʏ ɢʙᴀɴɴᴇᴅ ᴜꜱᴇʀꜱ!"
        )
        return

    banfile = "» ɢʙᴀɴɴᴇᴅ ᴜꜱᴇʀꜱ ʟɪꜱᴛ:\n\n"
    for user in banned_users:
        banfile += f"[x] {user['name']} - {user['user_id']}\n"
        if user["reason"]:
            banfile += f"Reason: {user['reason']}\n"

    with BytesIO(str.encode(banfile)) as output:
        output.name = "gbanlist.txt"
        update.effective_message.reply_document(
            document=output,
            filename="gbanlist.txt",
            caption="» ʜᴇʀᴇ ɪꜱ ᴛʜᴇ ʟɪꜱᴛ ᴏꜰ ᴄᴜʀʀᴇɴᴛʟʏ ɢʙᴀɴɴᴇᴅ ᴜꜱᴇʀꜱ.",
        )


def check_and_ban(update, user_id, should_message=True):
    if sql.is_user_gbanned(user_id):
        update.effective_chat.kick_member(user_id)
        if should_message:
            text = (
                f"⚠ 𝗔𝗹𝗲𝗿𝘁: <b>ᴛʜɪꜱ ᴜꜱᴇʀ ɪꜱ ɢʟᴏʙᴀʟʟʏ ʙᴀɴɴᴇᴅ.</b>\n\n"
                f"‣ <b>ʙᴀɴꜱ ᴛʜᴇᴍ ꜰʀᴏᴍ ʜᴇʀᴇ</b>.\n"
                f"‣ <b>ᴀᴘᴘᴇᴀʟ ᴄʜᴀᴛ</b>: @{SUPPORT_CHAT}\n"
                f"‣ <b>ᴜꜱᴇʀ ɪᴅ</b>: <code>{user_id}</code>"
            )
            user = sql.get_gbanned_user(user_id)
            if user.reason:
                text += f"\n‣ <b>ʙᴀɴ ʀᴇᴀꜱᴏɴ:</b> <code>{html.escape(user.reason)}</code>"
            update.effective_message.reply_text(text, parse_mode=ParseMode.HTML)


@run_async
def enforce_gban(update: Update, context: CallbackContext):
    # Not using @restrict handler to avoid spamming - just ignore if cant gban.
    bot = context.bot
    try:
        restrict_permission = update.effective_chat.get_member(
            bot.id
        ).can_restrict_members
    except Unauthorized:
        return
    if sql.does_chat_gban(update.effective_chat.id) and restrict_permission:
        user = update.effective_user
        chat = update.effective_chat
        msg = update.effective_message

        if user and not is_user_admin(chat, user.id):
            check_and_ban(update, user.id)
            return

        if msg.new_chat_members:
            new_members = update.effective_message.new_chat_members
            for mem in new_members:
                check_and_ban(update, mem.id)

        if msg.reply_to_message:
            user = msg.reply_to_message.from_user
            if user and not is_user_admin(chat, user.id):
                check_and_ban(update, user.id, should_message=False)


@run_async
@user_admin
def gbanstat(update: Update, context: CallbackContext):
    args = context.args
    if len(args) > 0:
        if args[0].lower() in ["on", "yes"]:
            sql.enable_gbans(update.effective_chat.id)
            update.effective_message.reply_text(
                "» ᴀɴᴛɪꜱᴘᴀᴍ ɪꜱ ɴᴏᴡ ᴇɴᴀʙʟᴇᴅ ✅"
                "» ɪ ᴀᴍ ɴᴏᴡ ᴘʀᴏᴛᴇᴄᴛɪɴɢ ʏᴏᴜʀ ɢʀᴏᴜᴘ ꜰʀᴏᴍ ᴘᴏᴛᴇɴᴛɪᴀʟ ʀᴇᴍᴏᴛᴇ ᴛʜʀᴇᴀᴛꜱ!"
            )
        elif args[0].lower() in ["off", "no"]:
            sql.disable_gbans(update.effective_chat.id)
            update.effective_message.reply_text(
                "» ᴀɴᴛɪꜱᴘᴀᴍ ɪꜱ ɴᴏᴡ ᴅɪꜱᴀʙʟᴇᴅ ❌" "» ꜱᴘᴀᴍᴡᴀᴛᴄʜ ɪꜱ ɴᴏᴡ ᴅɪꜱᴀʙʟᴇᴅ ❌"
            )
    else:
        update.effective_message.reply_text(
            "Give me some arguments to choose a setting! on/off, yes/no!\n\n"
            "Your current setting is: {}\n"
            "When True, any gbans that happen will also happen in your group. "
            "When False, they won't, leaving you at the possible mercy of "
            "spammers.".format(sql.does_chat_gban(update.effective_chat.id))
        )


def __stats__():
    return f"• {sql.num_gbanned_users()} ɢʙᴀɴɴᴇᴅ ᴜꜱᴇʀꜱ."


def __user_info__(user_id):
    is_gbanned = sql.is_user_gbanned(user_id)
    text = "» ᴍᴀʟɪᴄɪᴏᴜꜱ: <b>{}</b>"
    if user_id in [777000, 1087968824]:
        return ""
    if user_id == dispatcher.bot.id:
        return ""
    if int(user_id) in DRAGONS + TIGERS + WOLVES:
        return ""
    if is_gbanned:
        text = text.format("ʏᴇs")
        user = sql.get_gbanned_user(user_id)
        if user.reason:
            text += f"\n‣ <b>ʀᴇᴀꜱᴏɴ:</b> <code>{html.escape(user.reason)}</code>"
        text += f"\n‣ <b>ᴀᴘᴘᴇᴀʟ ᴄʜᴀᴛ:</b> @{SUPPORT_CHAT}"
    else:
        text = text.format("ɴᴏ")
    return text


def __migrate__(old_chat_id, new_chat_id):
    sql.migrate_chat(old_chat_id, new_chat_id)


def __chat_settings__(chat_id, user_id):
    return f"» ᴛʜɪꜱ ᴄʜᴀᴛ ɪꜱ ᴇɴꜰᴏʀᴄɪɴɢ **ɢʙᴀɴꜱ**: `{sql.does_chat_gban(chat_id)}`."


GBAN_HANDLER = CommandHandler("gban", gban)
UNGBAN_HANDLER = CommandHandler("ungban", ungban)
GBAN_LIST = CommandHandler("gbanlist", gbanlist)

GBAN_STATUS = CommandHandler("antispam", gbanstat, filters=Filters.group)

GBAN_ENFORCER = MessageHandler(Filters.all & Filters.group, enforce_gban)

dispatcher.add_handler(GBAN_HANDLER)
dispatcher.add_handler(UNGBAN_HANDLER)
dispatcher.add_handler(GBAN_LIST)
dispatcher.add_handler(GBAN_STATUS)

__mod_name__ = "Aɴᴛɪ-Sᴘᴀᴍ​"
__handlers__ = [GBAN_HANDLER, UNGBAN_HANDLER, GBAN_LIST, GBAN_STATUS]

if STRICT_GBAN:  # enforce GBANS if this is set
    dispatcher.add_handler(GBAN_ENFORCER, GBAN_ENFORCE_GROUP)
    __handlers__.append((GBAN_ENFORCER, GBAN_ENFORCE_GROUP))
