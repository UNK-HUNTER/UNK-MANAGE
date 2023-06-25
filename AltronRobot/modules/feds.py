# © @ItzExStar
# Copyright (c) 2022-2023 PythonX


import ast
import csv
import json
import os
import re
import time
import uuid
from io import BytesIO

import AltronRobot.modules.sql.feds_sql as sql
from AltronRobot import (
    EVENT_LOGS,
    LOGGER,
    SUPPORT_CHAT,
    OWNER_ID,
    DRAGONS,
    TIGERS,
    WOLVES,
    dispatcher,
)
from AltronRobot.modules.disable import DisableAbleCommandHandler
from AltronRobot.modules.helper_funcs.alternate import send_message
from AltronRobot.modules.helper_funcs.chat_status import is_user_admin
from AltronRobot.modules.helper_funcs.extraction import (
    extract_unt_fedban,
    extract_user,
    extract_user_fban,
)
from AltronRobot.modules.helper_funcs.string_handling import markdown_parser
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    MessageEntity,
    ParseMode,
    Update,
)
from telegram.error import BadRequest, TelegramError, Unauthorized
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    run_async
)
from telegram.utils.helpers import mention_html, mention_markdown

# Hello bot owner, I spended for feds many hours of my life, Please don't remove this if you still respect...🙃
# Federation update of Altron Robot v3 by PythonX 2022
# Total spended for making this features is 6+ hours


FBAN_ERRORS = {
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
    "Have no rights to send a message",
}

UNFBAN_ERRORS = {
    "User is an administrator of the chat",
    "Chat not found",
    "Not enough rights to restrict/unrestrict chat member",
    "User_not_participant",
    "Method is available for supergroup and channel chats only",
    "Not in the chat",
    "Channel_private",
    "Chat_admin_required",
    "Have no rights to send a message",
}


@run_async
def new_fed(update: Update, context: CallbackContext):
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message
    bot = context.bot

    if chat.type != "private":
        update.effective_message.reply_text(
            "Federations can only be created by privately messaging me.",
        )
        return
    if len(message.text) == 1:
        send_message(
            update.effective_message,
            "Please write the name of the federation!",
        )
        return
    try:
        fednam = message.text.split(None, 1)[1]
    except:
        update.effective_message.reply_text("𝗨𝘀𝗮𝗴𝗲:\n /newfed <ꜰᴇᴅ_ɴᴀᴍᴇ>")
        return
    if not fednam == "":
        fed_id = str(uuid.uuid4())
        fed_name = fednam
        LOGGER.info(fed_id)

        x = sql.new_fed(user.id, fed_name, fed_id)
        if not x:
            update.effective_message.reply_text(
                f"Can't federate! Please contact @{SUPPORT_CHAT} if the problem persist.",
            )
            return

        update.effective_message.reply_text(
            "*» ʏᴏᴜ ʜᴀᴠᴇ ꜱᴜᴄᴄᴇᴇᴅᴇᴅ ɪɴ ᴄʀᴇᴀᴛɪɴɢ ᴀ ɴᴇᴡ ꜰᴇᴅᴇʀᴀᴛɪᴏɴ!*"
            "\n• ɴᴀᴍᴇ: `{}`"
            "\n• ɪᴅ: `{}`"
            "\n\n» ᴜꜱᴇ ᴛʜᴇ ᴄᴏᴍᴍᴀɴᴅ ʙᴇʟᴏᴡ ᴛᴏ ᴊᴏɪɴ ᴛʜᴇ ꜰᴇᴅᴇʀᴀᴛɪᴏɴ:"
            "\n • `/joinfed {}`".format(fed_name, fed_id, fed_id),
            parse_mode=ParseMode.MARKDOWN,
        )
        try:
            bot.send_message(
                EVENT_LOGS,
                "» ɴᴇᴡ ꜰᴇᴅᴇʀᴀᴛɪᴏɴ: <b>{}</b>\n • ɪᴅ: <pre>{}</pre>".format(fed_name, fed_id),
                parse_mode=ParseMode.HTML,
            )
        except:
            LOGGER.warning("Cannot send a message to EVENT_LOGS")
    else:
        update.effective_message.reply_text("» ᴘʟᴇᴀꜱᴇ ᴡʀɪᴛᴇ ᴅᴏᴡɴ ᴛʜᴇ ɴᴀᴍᴇ ᴏꜰ ᴛʜᴇ ꜰᴇᴅᴇʀᴀᴛɪᴏɴ",)


@run_async
def del_fed(update: Update, context: CallbackContext):
    args = context.args
    chat = update.effective_chat
    user = update.effective_user
    if chat.type != "private":
        update.effective_message.reply_text(
            "Federations can only be deleted by privately messaging me.",
        )
        return
    if args:
        is_fed_id = args[0]
        getinfo = sql.get_fed_info(is_fed_id)
        if getinfo is False:
            update.effective_message.reply_text("» ᴛʜɪꜱ ꜰᴇᴅᴇʀᴀᴛɪᴏɴ ᴅᴏᴇꜱ ɴᴏᴛ ᴇxɪꜱᴛ.")
            return
        if int(getinfo["owner"]) == int(user.id) or int(user.id) == OWNER_ID:
            fed_id = is_fed_id
        else:
            update.effective_message.reply_text("Only federation owners can do this!")
            return
    else:
        update.effective_message.reply_text("What should I delete?")
        return

    if is_user_fed_owner(fed_id, user.id) is False:
        update.effective_message.reply_text("Only federation owners can do this!")
        return

    update.effective_message.reply_text(
        "» ᴀʀᴇ ʏᴏᴜ ꜱᴜʀᴇ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴅᴇʟᴇᴛᴇ ʏᴏᴜʀ ꜰᴇᴅᴇʀᴀᴛɪᴏɴ? ᴛʜɪꜱ ᴄᴀɴɴᴏᴛ ʙᴇ ʀᴇᴠᴇʀᴛᴇᴅ, ʏᴏᴜ ᴡɪʟʟ ʟᴏꜱᴇ ʏᴏᴜʀ ᴇɴᴛɪʀᴇ ʙᴀɴ ʟɪꜱᴛ, ᴀɴᴅ '{}' ᴡɪʟʟ ʙᴇ ᴘᴇʀᴍᴀɴᴇɴᴛʟʏ ʟᴏꜱᴛ.".format(
            getinfo["fname"],
        ),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="⚠️ ᴅᴇʟᴇᴛᴇ ꜰᴇᴅ",
                        callback_data="rmfed_{}".format(fed_id),
                    ),
                InlineKeyboardButton(text="❌ ᴄᴀɴᴄᴇʟ", callback_data="rmfed_cancel"),
                ],
            ],
        ),
    )


@run_async
def rename_fed(update, context):
    user = update.effective_user
    msg = update.effective_message
    args = msg.text.split(None, 2)

    if len(args) < 3:
        return msg.reply_text("𝗨𝘀𝗮𝗴𝗲:\n  /renamefed <ꜰᴇᴅ_ɪᴅ> <ɴᴇᴡɴᴀᴍᴇ>")

    fed_id, newname = args[1], args[2]
    verify_fed = sql.get_fed_info(fed_id)

    if not verify_fed:
        return msg.reply_text("» ᴛʜɪꜱ ꜰᴇᴅ ɴᴏᴛ ᴇxɪꜱᴛ ɪɴ ᴍʏ ᴅᴀᴛᴀʙᴀꜱᴇ!")

    if is_user_fed_owner(fed_id, user.id):
        sql.rename_fed(fed_id, user.id, newname)
        msg.reply_text(f"» ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ʀᴇɴᴀᴍᴇᴅ ʏᴏᴜʀ ꜰᴇᴅ ɴᴀᴍᴇ ᴛᴏ {newname}!")
    else:
        msg.reply_text("Only federation owner can do this!")


@run_async
def fed_chat(update: Update, context: CallbackContext):
    chat = update.effective_chat
    fed_id = sql.get_fed_id(chat.id)

    user_id = update.effective_message.from_user.id
    if not is_user_admin(update.effective_chat, user_id):
        update.effective_message.reply_text("You must be an admin to execute this command",)
        return

    if not fed_id:
        update.effective_message.reply_text("» ᴛʜɪꜱ ɢʀᴏᴜᴘ ɪꜱ ɴᴏᴛ ɪɴ ᴀɴʏ ꜰᴇᴅᴇʀᴀᴛɪᴏɴ!")
        return

    chat = update.effective_chat
    info = sql.get_fed_info(fed_id)

    text = "<b>» ᴛʜɪꜱ ɢʀᴏᴜᴘ ɪꜱ ᴘᴀʀᴛ ᴏꜰ ᴛʜᴇ ꜰᴏʟʟᴏᴡɪɴɢ ꜰᴇᴅᴇʀᴀᴛɪᴏɴ:</b>\n"
    text += "‣ \n{}\n ɪᴅ: <code>{}</code>".format(info["fname"], fed_id)

    update.effective_message.reply_text(text, parse_mode=ParseMode.HTML)


@run_async
def join_fed(update: Update, context: CallbackContext):
    bot, args = context.bot, context.args
    chat = update.effective_chat
    user = update.effective_user

    if chat.type == "private":
        send_message(
            update.effective_message,
            "This command is specific to the group, not to our pm!",
        )
        return

    message = update.effective_message
    administrators = chat.get_administrators()
    fed_id = sql.get_fed_id(chat.id)

    if user.id in DRAGONS:
        pass
    else:
        for admin in administrators:
            status = admin.status
            if status == "creator":
                if str(admin.user.id) == str(user.id):
                    pass
                else:
                    update.effective_message.reply_text(
                        "Only group creators can use this command!",
                    )
                    return
    if fed_id:
        message.reply_text("» ʏᴏᴜ ᴄᴀɴɴᴏᴛ ᴊᴏɪɴ ᴛᴡᴏ ꜰᴇᴅᴇʀᴀᴛɪᴏɴꜱ ꜰʀᴏᴍ ᴏɴᴇ ᴄʜᴀᴛ!")
        return

    if len(args) >= 1:
        getfed = sql.search_fed_by_id(args[0])
        if getfed is False:
            message.reply_text("» ᴘʟᴇᴀꜱᴇ ᴇɴᴛᴇʀ ᴀ ᴠᴀʟɪᴅ ꜰᴇᴅᴇʀᴀᴛɪᴏɴ ɪᴅ.")
            return

        x = sql.chat_join_fed(args[0], chat.title, chat.id)
        if not x:
            message.reply_text(
                f"Failed to join federation! Please contact @{SUPPORT_CHAT} should this problem persist!",
            )
            return

        get_fedlog = sql.get_fed_log(args[0])
        if get_fedlog:
            if ast.literal_eval(get_fedlog):
                bot.send_message(
                    get_fedlog,
                    "» ᴄʜᴀᴛ *{}* ʜᴀꜱ ᴊᴏɪɴᴇᴅ ᴛʜᴇ ꜰᴇᴅᴇʀᴀᴛɪᴏɴ *{}*".format(
                        chat.title,
                        getfed["fname"],
                    ),
                    parse_mode="markdown",
                )

        message.reply_text(
            "» ᴛʜɪꜱ ɢʀᴏᴜᴘ ʜᴀꜱ ᴊᴏɪɴᴇᴅ ᴛʜᴇ ꜰᴇᴅᴇʀᴀᴛɪᴏɴ: {}!".format(getfed["fname"]),
        )


@run_async
def leave_fed(update: Update, context: CallbackContext):
    bot = context.bot
    chat = update.effective_chat
    user = update.effective_user

    if chat.type == "private":
        send_message(
            update.effective_message,
            "This command is specific to the group, not to our PM!",
        )
        return

    fed_id = sql.get_fed_id(chat.id)
    fed_info = sql.get_fed_info(fed_id)

    # administrators = chat.get_administrators().status
    getuser = bot.get_chat_member(chat.id, user.id).status
    if getuser in "creator" or user.id in DRAGONS:
        if sql.chat_leave_fed(chat.id) is True:
            get_fedlog = sql.get_fed_log(fed_id)
            if get_fedlog:
                if ast.literal_eval(get_fedlog):
                    bot.send_message(
                        get_fedlog,
                        "» ᴄʜᴀᴛ *{}* ʜᴀꜱ ʟᴇꜰᴛ ᴛʜᴇ ꜰᴇᴅᴇʀᴀᴛɪᴏɴ *{}*".format(
                            chat.title,
                            fed_info["fname"],
                        ),
                        parse_mode="markdown",
                    )
            send_message(
                update.effective_message,
                "» ᴛʜɪꜱ ɢʀᴏᴜᴘ ʜᴀꜱ ʟᴇꜰᴛ ᴛʜᴇ ꜰᴇᴅᴇʀᴀᴛɪᴏɴ {}!".format(fed_info["fname"]),
            )
        else:
            update.effective_message.reply_text(
                "How can you leave a federation that you never joined?!",
            )
    else:
        update.effective_message.reply_text("Only group creators can use this command!")


@run_async
def user_join_fed(update: Update, context: CallbackContext):
    bot, args = context.bot, context.args
    chat = update.effective_chat
    user = update.effective_user
    msg = update.effective_message

    if chat.type == "private":
        send_message(
            update.effective_message,
            "This command is specific to the group, not to our pm!",
        )
        return

    fed_id = sql.get_fed_id(chat.id)

    if is_user_fed_owner(fed_id, user.id) or user.id in DRAGONS:
        user_id = extract_user(msg, args)
        if user_id:
            user = bot.get_chat(user_id)
        elif not msg.reply_to_message and not args:
            user = msg.from_user
        elif not msg.reply_to_message and (
            not args
            or (
                len(args) >= 1
                and not args[0].startswith("@")
                and not args[0].isdigit()
                and not msg.parse_entities([MessageEntity.TEXT_MENTION])
            )
        ):
            msg.reply_text("I cannot extract user from this message")
            return
        else:
            LOGGER.warning("error")
        getuser = sql.search_user_in_fed(fed_id, user_id)
        fed_id = sql.get_fed_id(chat.id)
        info = sql.get_fed_info(fed_id)
        get_owner = ast.literal_eval(info["fusers"])["owner"]
        get_owner = bot.get_chat(get_owner).id
        if user_id == get_owner:
            update.effective_message.reply_text(
                "You do know that the user is the federation owner, right? RIGHT?",
            )
            return
        if getuser:
            update.effective_message.reply_text(
                "I cannot promote users who are already federation admins! Can remove them if you want!",
            )
            return
        if user_id == bot.id:
            update.effective_message.reply_text(
                "I already am a federation admin in all federations!",
            )
            return
        res = sql.user_join_fed(fed_id, user_id)
        if res:
            update.effective_message.reply_text("» ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ᴘʀᴏᴍᴏᴛᴇᴅ!")
        else:
            update.effective_message.reply_text("» ꜰᴀɪʟᴇᴅ ᴛᴏ ᴘʀᴏᴍᴏᴛᴇ!")
    else:
        update.effective_message.reply_text("Only federation owners can do this!")


@run_async
def user_demote_fed(update: Update, context: CallbackContext):
    bot, args = context.bot, context.args
    chat = update.effective_chat
    user = update.effective_user

    if chat.type == "private":
        send_message(
            update.effective_message,
            "This command is specific to the group, not to our pm!",
        )
        return

    fed_id = sql.get_fed_id(chat.id)

    if is_user_fed_owner(fed_id, user.id):
        msg = update.effective_message
        user_id = extract_user(msg, args)
        if user_id:
            user = bot.get_chat(user_id)

        elif not msg.reply_to_message and not args:
            user = msg.from_user

        elif not msg.reply_to_message and (
            not args
            or (
                len(args) >= 1
                and not args[0].startswith("@")
                and not args[0].isdigit()
                and not msg.parse_entities([MessageEntity.TEXT_MENTION])
            )
        ):
            msg.reply_text("I cannot extract user from this message")
            return
        else:
            LOGGER.warning("error")

        if user_id == bot.id:
            update.effective_message.reply_text(
                "The thing you are trying to demote me from will fail to work without me! Just saying.",
            )
            return

        if sql.search_user_in_fed(fed_id, user_id) is False:
            update.effective_message.reply_text(
                "I cannot demote people who are not federation admins!",
            )
            return

        res = sql.user_demote_fed(fed_id, user_id)
        if res is True:
            update.effective_message.reply_text("» ᴅᴇᴍᴏᴛᴇᴅ ꜰʀᴏᴍ ᴀ ꜰᴇᴅ ᴀᴅᴍɪɴ!")
        else:
            update.effective_message.reply_text("» ᴅᴇᴍᴏᴛɪᴏɴ ꜰᴀɪʟᴇᴅ!")
    else:
        update.effective_message.reply_text("Only federation owners can do this!")
        return


@run_async
def fed_info(update: Update, context: CallbackContext):
    bot, args = context.bot, context.args
    chat = update.effective_chat
    user = update.effective_user
    if args:
        fed_id = args[0]
        info = sql.get_fed_info(fed_id)
    else:
        if chat.type == "private":
            send_message(
                update.effective_message,
                "You need to provide me a fedid to check fedinfo in my pm.",
            )
            return
        fed_id = sql.get_fed_id(chat.id)
        if not fed_id:
            send_message(
                update.effective_message,
                "» ᴛʜɪꜱ ɢʀᴏᴜᴘ ɪꜱ ɴᴏᴛ ɪɴ ᴀɴʏ ꜰᴇᴅᴇʀᴀᴛɪᴏɴ!",
            )
            return
        info = sql.get_fed_info(fed_id)

    if is_user_fed_admin(fed_id, user.id) is False:
        update.effective_message.reply_text("Only a federation admin can do this!")
        return

    owner = bot.get_chat(info["owner"])
    try:
        owner_name = owner.first_name + " " + owner.last_name
    except:
        owner_name = owner.first_name
    FEDADMIN = sql.all_fed_users(fed_id)
    TotalAdminFed = len(FEDADMIN)

    user = update.effective_user
    chat = update.effective_chat
    info = sql.get_fed_info(fed_id)

    text = "<b>» ꜰᴇᴅᴇʀᴀᴛɪᴏɴ ɪɴꜰᴏʀᴍᴀᴛɪᴏɴ:</b>"
    text += "\n • ꜰᴇᴅ-ɪᴅ: <code>{}</code>".format(fed_id)
    text += "\n • ɴᴀᴍᴇ: {}".format(info["fname"])
    text += "\n • ᴄʀᴇᴀᴛᴏʀ: {}".format(mention_html(owner.id, owner_name))
    text += "\n • ᴀʟʟ ᴀᴅᴍɪɴꜱ: <code>{}</code>".format(TotalAdminFed)
    getfban = sql.get_all_fban_users(fed_id)
    text += "\n • ᴛᴏᴛᴀʟ ʙᴀɴɴᴇᴅ ᴜꜱᴇʀꜱ: <code>{}</code>".format(len(getfban))
    getfchat = sql.all_fed_chats(fed_id)
    text += "\n • ɴᴜᴍʙᴇʀ ᴏꜰ ɢʀᴏᴜᴘꜱ ɪɴ ᴛʜɪꜱ ꜰᴇᴅᴇʀᴀᴛɪᴏɴ: <code>{}</code>".format(
        len(getfchat),
    )

    update.effective_message.reply_text(text, parse_mode=ParseMode.HTML)


@run_async
def fed_admin(update: Update, context: CallbackContext):
    bot = context.bot
    chat = update.effective_chat
    user = update.effective_user

    if chat.type == "private":
        send_message(
            update.effective_message,
            "This command is specific to the group, not to our pm!",
        )
        return

    fed_id = sql.get_fed_id(chat.id)

    if not fed_id:
        update.effective_message.reply_text("» ᴛʜɪꜱ ɢʀᴏᴜᴘ ɪꜱ ɴᴏᴛ ɪɴ ᴀɴʏ ꜰᴇᴅᴇʀᴀᴛɪᴏɴ!")
        return

    if is_user_fed_admin(fed_id, user.id) is False:
        update.effective_message.reply_text("Only federation admins can do this!")
        return

    user = update.effective_user
    chat = update.effective_chat
    info = sql.get_fed_info(fed_id)

    text = "<b>» ꜰᴇᴅᴇʀᴀᴛɪᴏɴ ᴀᴅᴍɪɴ {}:</b>\n\n".format(info["fname"])
    text += "👑 Oᴡɴᴇʀ:\n"
    owner = bot.get_chat(info["owner"])
    try:
        owner_name = owner.first_name + " " + owner.last_name
    except:
        owner_name = owner.first_name
    text += " • {}\n".format(mention_html(owner.id, owner_name))

    members = sql.all_fed_members(fed_id)
    if len(members) == 0:
        text += "\n» ᴛʜᴇʀᴇ ᴀʀᴇ ɴᴏ ᴀᴅᴍɪɴꜱ ɪɴ ᴛʜɪꜱ ꜰᴇᴅᴇʀᴀᴛɪᴏɴ."
    else:
        text += "\n🔱 Aᴅᴍɪɴ:\n"
        for x in members:
            user = bot.get_chat(x)
            text += " • {}\n".format(mention_html(user.id, user.first_name))

    update.effective_message.reply_text(text, parse_mode=ParseMode.HTML)


@run_async
def fed_ban(update: Update, context: CallbackContext):
    bot, args = context.bot, context.args
    chat = update.effective_chat
    user = update.effective_user

    if chat.type == "private":
        send_message(
            update.effective_message,
            "This command is specific to the group, not to our pm!",
        )
        return

    fed_id = sql.get_fed_id(chat.id)

    if not fed_id:
        update.effective_message.reply_text(
            "» ᴛʜɪꜱ ɢʀᴏᴜᴘ ɪꜱ ɴᴏᴛ ᴀ ᴘᴀʀᴛ ᴏꜰ ᴀɴʏ ꜰᴇᴅᴇʀᴀᴛɪᴏɴ!",
        )
        return

    info = sql.get_fed_info(fed_id)
    getfednotif = sql.user_feds_report(info["owner"])

    if is_user_fed_admin(fed_id, user.id) is False:
        update.effective_message.reply_text("Only federation admins can do this!")
        return

    message = update.effective_message

    user_id, reason = extract_unt_fedban(message, args)

    fban, fbanreason, fbantime = sql.get_fban_user(fed_id, user_id)

    if not user_id:
        message.reply_text("You don't seem to be referring to a user")
        return

    if user_id == bot.id:
        message.reply_text(
            "What is funnier than kicking the group creator? Self sacrifice.",
        )
        return

    if is_user_fed_owner(fed_id, user_id) is True:
        message.reply_text("Why did you try the federation fban?")
        return

    if is_user_fed_admin(fed_id, user_id) is True:
        message.reply_text("He is a federation admin, I can't fban him.")
        return

    if user_id == OWNER_ID:
        message.reply_text("Disaster level God cannot be fed banned!")
        return

    if int(user_id) in DRAGONS:
        message.reply_text("Dragons cannot be fed banned!")
        return

    if int(user_id) in TIGERS:
        message.reply_text("Tigers cannot be fed banned!")
        return

    if int(user_id) in WOLVES:
        message.reply_text("Wolves cannot be fed banned!")
        return

    if user_id in [777000, 1087968824]:
        message.reply_text("Fool! You can't attack Telegram's native tech!")
        return

    try:
        user_chat = bot.get_chat(user_id)
        isvalid = True
        fban_user_id = user_chat.id
        fban_user_name = user_chat.first_name
        fban_user_lname = user_chat.last_name
        fban_user_uname = user_chat.username
    except BadRequest as excp:
        if not str(user_id).isdigit():
            send_message(update.effective_message, excp.message)
            return
        if len(str(user_id)) != 9:
            send_message(update.effective_message, "That's so not a user!")
            return
        isvalid = False
        fban_user_id = int(user_id)
        fban_user_name = "user({})".format(user_id)
        fban_user_lname = None
        fban_user_uname = None

    if isvalid and user_chat.type != "private":
        send_message(update.effective_message, "That's so not a user!")
        return

    if isvalid:
        user_target = mention_html(fban_user_id, fban_user_name)
    else:
        user_target = fban_user_name

    if fban:
        fed_name = info["fname"]

        temp = sql.un_fban_user(fed_id, fban_user_id)
        if not temp:
            message.reply_text("Failed to update the reason for fedban!")
            return
        x = sql.fban_user(
            fed_id,
            fban_user_id,
            fban_user_name,
            fban_user_lname,
            fban_user_uname,
            reason,
            int(time.time()),
        )
        if not x:
            message.reply_text(
                f"Failed to ban from the federation! If this problem continues, contact @{SUPPORT_CHAT}.",
            )
            return

        fed_chats = sql.all_fed_chats(fed_id)
        NewReason = "<b>❕ ꜰᴇᴅʙᴀɴ ʀᴇᴀꜱᴏɴ ᴜᴘᴅᴀᴛᴇᴅ</b>\n<b> • ꜰᴇᴅᴇʀᴀᴛɪᴏɴ:</b> {}\n<b> • ꜰᴇᴅᴇʀᴀᴛɪᴏɴ ᴀᴅᴍɪɴ:</b> {}\n<b> • ᴜꜱᴇʀ:</b> {}\n<b> • ᴜꜱᴇʀ ɪᴅ:</b> <code>{}</code>\n<b> • ʀᴇᴀꜱᴏɴ:</b> {}".format(
                fed_name,
                mention_html(user.id, user.first_name),
                user_target,
                fban_user_id,
                reason,
            )
        # Will send to current chat
        bot.send_message(chat.id, NewReason, parse_mode="HTML",)
        # Send message to owner if fednotif is enabled
        if getfednotif:
            bot.send_message(info["owner"], NewReason, parse_mode="HTML",)
        # If fedlog is set, then send message, except fedlog is current chat
        get_fedlog = sql.get_fed_log(fed_id)
        if get_fedlog:
            if int(get_fedlog) != int(chat.id):
                bot.send_message(get_fedlog, NewReason, parse_mode="HTML",)
        for fedschat in fed_chats:
            try:
                bot.kick_chat_member(fedschat, fban_user_id)
            except BadRequest as excp:
                if excp.message in FBAN_ERRORS:
                    try:
                        dispatcher.bot.getChat(fedschat)
                    except Unauthorized:
                        sql.chat_leave_fed(fedschat)
                        LOGGER.info(
                            "Chat {} has leave fed {} because I was kicked".format(
                                fedschat,
                                info["fname"],
                            ),
                        )
                        continue
                elif excp.message == "User_id_invalid":
                    break
                else:
                    LOGGER.warning(
                        "Could not fban on {} because: {}".format(chat, excp.message),
                    )
            except TelegramError:
                pass

        # Fban for fed subscriber
        subscriber = list(sql.get_subscriber(fed_id))
        if len(subscriber) != 0:
            for fedsid in subscriber:
                all_fedschat = sql.all_fed_chats(fedsid)
                for fedschat in all_fedschat:
                    try:
                        bot.kick_chat_member(fedschat, fban_user_id)
                    except BadRequest as excp:
                        if excp.message in FBAN_ERRORS:
                            try:
                                dispatcher.bot.getChat(fedschat)
                            except Unauthorized:
                                targetfed_id = sql.get_fed_id(fedschat)
                                sql.unsubs_fed(fed_id, targetfed_id)
                                LOGGER.info(
                                    "Chat {} has unsub fed {} because I was kicked".format(
                                        fedschat,
                                        info["fname"],
                                    ),
                                )
                                continue
                        elif excp.message == "User_id_invalid":
                            break
                        else:
                            LOGGER.warning(
                                "Unable to fban on {} because: {}".format(
                                    fedschat,
                                    excp.message,
                                ),
                            )
                    except TelegramError:
                        pass
        return

    fed_name = info["fname"]

    x = sql.fban_user(
        fed_id,
        fban_user_id,
        fban_user_name,
        fban_user_lname,
        fban_user_uname,
        reason,
        int(time.time()),
    )
    if not x:
        message.reply_text(
            f"Failed to ban from the federation! If this problem continues, contact @{SUPPORT_CHAT}.",
        )
        return

    fed_chats = sql.all_fed_chats(fed_id)
    BanText = "<b>❕ ɴᴇᴡ ꜰᴇᴅʙᴀɴ</b>\n<b> • ꜰᴇᴅᴇʀᴀᴛɪᴏɴ:</b> {}\n<b> • ꜰᴇᴅᴇʀᴀᴛɪᴏɴ ᴀᴅᴍɪɴ:</b> {}\n<b> • ᴜꜱᴇʀ:</b> {}\n<b> • ᴜꜱᴇʀ ɪᴅ:</b> <code>{}</code>\n<b> • ʀᴇᴀꜱᴏɴ:</b> {}".format(
            fed_name,
            mention_html(user.id, user.first_name),
            user_target,
            fban_user_id,
            reason,
        )
    # Will send to current chat
    bot.send_message(chat.id, BanText, parse_mode="HTML",)
    # Send message to owner if fednotif is enabled
    if getfednotif:
        bot.send_message(info["owner"], BanText, parse_mode="HTML",)
    # If fedlog is set, then send message, except fedlog is current chat
    get_fedlog = sql.get_fed_log(fed_id)
    if get_fedlog:
        if int(get_fedlog) != int(chat.id):
            bot.send_message(get_fedlog, BanText, parse_mode="HTML",)
    chats_in_fed = 0
    for fedschat in fed_chats:
        chats_in_fed += 1
        try:
            bot.kick_chat_member(fedschat, fban_user_id)
        except BadRequest as excp:
            if excp.message in FBAN_ERRORS:
                pass
            elif excp.message == "User_id_invalid":
                break
            else:
                LOGGER.warning(
                    "Could not fban on {} because: {}".format(chat, excp.message),
                )
        except TelegramError:
            pass

        # Fban for fed subscriber
        subscriber = list(sql.get_subscriber(fed_id))
        if len(subscriber) != 0:
            for fedsid in subscriber:
                all_fedschat = sql.all_fed_chats(fedsid)
                for fedschat in all_fedschat:
                    try:
                        bot.kick_chat_member(fedschat, fban_user_id)
                    except BadRequest as excp:
                        if excp.message in FBAN_ERRORS:
                            try:
                                dispatcher.bot.getChat(fedschat)
                            except Unauthorized:
                                targetfed_id = sql.get_fed_id(fedschat)
                                sql.unsubs_fed(fed_id, targetfed_id)
                                LOGGER.info(
                                    "Chat {} has unsub fed {} because I was kicked".format(
                                        fedschat,
                                        info["fname"],
                                    ),
                                )
                                continue
                        elif excp.message == "User_id_invalid":
                            break
                        else:
                            LOGGER.warning(
                                "Unable to fban on {} because: {}".format(
                                    fedschat,
                                    excp.message,
                                ),
                            )
                    except TelegramError:
                        pass


@run_async
def unfban(update: Update, context: CallbackContext):
    bot, args = context.bot, context.args
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message

    if chat.type == "private":
        send_message(
            update.effective_message,
            "This command is specific to the group, not to our pm!",
        )
        return

    fed_id = sql.get_fed_id(chat.id)

    if not fed_id:
        update.effective_message.reply_text(
            "» ᴛʜɪꜱ ɢʀᴏᴜᴘ ɪꜱ ɴᴏᴛ ᴀ ᴘᴀʀᴛ ᴏꜰ ᴀɴʏ ꜰᴇᴅᴇʀᴀᴛɪᴏɴ!",
        )
        return

    info = sql.get_fed_info(fed_id)
    getfednotif = sql.user_feds_report(info["owner"])

    if is_user_fed_admin(fed_id, user.id) is False:
        update.effective_message.reply_text("Only federation admins can do this!")
        return

    user_id = extract_user_fban(message, args)
    if not user_id:
        message.reply_text("You do not seem to be referring to a user.")
        return

    try:
        user_chat = bot.get_chat(user_id)
        isvalid = True
        fban_user_id = user_chat.id
        fban_user_name = user_chat.first_name
    except BadRequest as excp:
        if not str(user_id).isdigit():
            send_message(update.effective_message, excp.message)
            return
        if len(str(user_id)) != 9:
            send_message(update.effective_message, "That's so not a user!")
            return
        isvalid = False
        fban_user_id = int(user_id)
        fban_user_name = "user({})".format(user_id)

    if isvalid and user_chat.type != "private":
        message.reply_text("That's so not a user!")
        return

    if isvalid:
        user_target = mention_html(fban_user_id, fban_user_name)
    else:
        user_target = fban_user_name

    fban, fbanreason, fbantime = sql.get_fban_user(fed_id, fban_user_id)
    if fban is False:
        message.reply_text("» ᴛʜɪꜱ ᴜꜱᴇʀ ɪꜱ ɴᴏᴛ ꜰʙᴀɴɴᴇᴅ!")
        return

    chat_list = sql.all_fed_chats(fed_id)
    UnBanText = "<b>❕ ᴜɴ-ꜰᴇᴅʙᴀɴ</b>\n<b> • ꜰᴇᴅᴇʀᴀᴛɪᴏɴ:</b> {}\n<b> • ꜰᴇᴅᴇʀᴀᴛɪᴏɴ ᴀᴅᴍɪɴ:</b> {}\n<b> • ᴜꜱᴇʀ:</b> {}\n<b> • ᴜꜱᴇʀ ɪᴅ:</b> <code>{}</code>".format(
                info["fname"],
                mention_html(user.id, user.first_name),
                user_target,
                fban_user_id,
            )
    
    # Will send to current chat
    bot.send_message(chat.id, UnBanText, parse_mode="HTML",)
    # Send message to owner if fednotif is enabled
    if getfednotif:
        bot.send_message(info["owner"], UnBanText, parse_mode="HTML",)
    # If fedlog is set, then send message, except fedlog is current chat
    get_fedlog = sql.get_fed_log(fed_id)
    if get_fedlog:
        if int(get_fedlog) != int(chat.id):
            bot.send_message(get_fedlog, UnBanText, parse_mode="HTML",)
    unfbanned_in_chats = 0
    for fedchats in chat_list:
        unfbanned_in_chats += 1
        try:
            member = bot.get_chat_member(fedchats, user_id)
            if member.status == "kicked":
                bot.unban_chat_member(fedchats, user_id)
        except BadRequest as excp:
            if excp.message in UNFBAN_ERRORS:
                pass
            elif excp.message == "User_id_invalid":
                break
            else:
                LOGGER.warning(
                    "Could not fban on {} because: {}".format(chat, excp.message),
                )
        except TelegramError:
            pass

    try:
        x = sql.un_fban_user(fed_id, user_id)
        if not x:
            send_message(
                update.effective_message,
                "» ᴜɴ-ꜰʙᴀɴ ꜰᴀɪʟᴇᴅ, ᴛʜɪꜱ ᴜꜱᴇʀ ᴍᴀʏ ᴀʟʀᴇᴀᴅʏ ʙᴇ ᴜɴ-ꜰᴇᴅʙᴀɴɴᴇᴅ!",
            )
            return
    except:
        pass

    # UnFban for fed subscriber
    subscriber = list(sql.get_subscriber(fed_id))
    if len(subscriber) != 0:
        for fedsid in subscriber:
            all_fedschat = sql.all_fed_chats(fedsid)
            for fedschat in all_fedschat:
                try:
                    bot.unban_chat_member(fedchats, user_id)
                except BadRequest as excp:
                    if excp.message in FBAN_ERRORS:
                        try:
                            dispatcher.bot.getChat(fedschat)
                        except Unauthorized:
                            targetfed_id = sql.get_fed_id(fedschat)
                            sql.unsubs_fed(fed_id, targetfed_id)
                            LOGGER.info(
                                "Chat {} has unsub fed {} because I was kicked".format(
                                    fedschat,
                                    info["fname"],
                                ),
                            )
                            continue
                    elif excp.message == "User_id_invalid":
                        break
                    else:
                        LOGGER.warning(
                            "Unable to fban on {} because: {}".format(
                                fedschat,
                                excp.message,
                            ),
                        )
                except TelegramError:
                    pass

    if unfbanned_in_chats == 0:
        send_message(
            update.effective_message,
            "» ᴛʜɪꜱ ᴘᴇʀꜱᴏɴ ʜᴀꜱ ʙᴇᴇɴ ᴜɴ-ꜰʙᴀɴɴᴇᴅ ɪɴ 0 ᴄʜᴀᴛꜱ.",
        )
    if unfbanned_in_chats > 0:
        send_message(
            update.effective_message,
            "» ᴛʜɪꜱ ᴘᴇʀꜱᴏɴ ʜᴀꜱ ʙᴇᴇɴ ᴜɴ-ꜰʙᴀɴɴᴇᴅ ɪɴ {} ᴄʜᴀᴛꜱ.".format(unfbanned_in_chats),
        )


@run_async
def set_frules(update: Update, context: CallbackContext):
    bot, args = context.bot, context.args
    chat = update.effective_chat
    user = update.effective_user

    if chat.type == "private":
        send_message(
            update.effective_message,
            "This command is specific to the group, not to our pm!",
        )
        return

    fed_id = sql.get_fed_id(chat.id)

    if not fed_id:
        update.effective_message.reply_text("» ᴛʜɪꜱ ɢʀᴏᴜᴘ ɪꜱ ɴᴏᴛ ɪɴ ᴀɴʏ ꜰᴇᴅᴇʀᴀᴛɪᴏɴ!")
        return

    if is_user_fed_admin(fed_id, user.id) is False:
        update.effective_message.reply_text("Only fed admins can do this!")
        return

    if len(args) >= 1:
        msg = update.effective_message
        raw_text = msg.text
        args = raw_text.split(None, 1)  # use python's maxsplit to separate cmd and args
        if len(args) == 2:
            txt = args[1]
            offset = len(txt) - len(raw_text)  # set correct offset relative to command
            markdown_rules = markdown_parser(
                txt,
                entities=msg.parse_entities(),
                offset=offset,
            )
        x = sql.set_frules(fed_id, markdown_rules)
        if not x:
            update.effective_message.reply_text(
                f"Whoa! There was an error while setting federation rules! If you wondered why please ask it in @{SUPPORT_CHAT}!",
            )
            return

        rules = sql.get_fed_info(fed_id)["frules"]
        getfed = sql.get_fed_info(fed_id)
        get_fedlog = sql.get_fed_log(fed_id)
        if get_fedlog:
            if ast.literal_eval(get_fedlog):
                bot.send_message(
                    get_fedlog,
                    "» *{}* ʜᴀꜱ ᴜᴘᴅᴀᴛᴇᴅ ꜰᴇᴅᴇʀᴀᴛɪᴏɴ ʀᴜʟᴇꜱ ꜰᴏʀ ꜰᴇᴅ *{}*".format(
                        user.first_name,
                        getfed["fname"],
                    ),
                    parse_mode="markdown",
                )
        update.effective_message.reply_text(f"» ʀᴜʟᴇꜱ ʜᴀᴠᴇ ʙᴇᴇɴ ᴄʜᴀɴɢᴇᴅ ᴛᴏ :\n{rules}!")
    else:
        update.effective_message.reply_text("Please write rules to set this up!")


@run_async
def get_frules(update: Update, context: CallbackContext):
    chat = update.effective_chat

    if chat.type == "private":
        send_message(
            update.effective_message,
            "This command is specific to the group, not to our pm!",
        )
        return

    fed_id = sql.get_fed_id(chat.id)
    if not fed_id:
        update.effective_message.reply_text("» ᴛʜɪꜱ ɢʀᴏᴜᴘ ɪꜱ ɴᴏᴛ ɪɴ ᴀɴʏ ꜰᴇᴅᴇʀᴀᴛɪᴏɴ!")
        return

    rules = sql.get_frules(fed_id)
    text = "*» ʀᴜʟᴇꜱ ɪɴ ᴛʜɪꜱ ꜰᴇᴅ:*\n"
    text += rules
    update.effective_message.reply_text(text, parse_mode=ParseMode.MARKDOWN)


@run_async
def fed_broadcast(update: Update, context: CallbackContext):
    bot, args = context.bot, context.args
    msg = update.effective_message
    user = update.effective_user
    chat = update.effective_chat

    if chat.type == "private":
        send_message(
            update.effective_message,
            "This command is specific to the group, not to our pm!",
        )
        return

    if args:
        chat = update.effective_chat
        fed_id = sql.get_fed_id(chat.id)
        fedinfo = sql.get_fed_info(fed_id)
        if is_user_fed_owner(fed_id, user.id) is False:
            update.effective_message.reply_text("Only federation owners can do this!")
            return
        # Parsing md
        raw_text = msg.text
        args = raw_text.split(None, 1)  # use python's maxsplit to separate cmd and args
        txt = args[1]
        offset = len(txt) - len(raw_text)  # set correct offset relative to command
        text_parser = markdown_parser(txt, entities=msg.parse_entities(), offset=offset)
        text = text_parser
        try:
            broadcaster = user.first_name
        except:
            broadcaster = user.first_name + " " + user.last_name
        text += "\n\n- {}".format(mention_markdown(user.id, broadcaster))
        chat_list = sql.all_fed_chats(fed_id)
        failed = 0
        for chat in chat_list:
            title = "*» ɴᴇᴡ ʙʀᴏᴀᴅᴄᴀꜱᴛ ꜰʀᴏᴍ ꜰᴇᴅ {}*\n".format(fedinfo["fname"])
            try:
                bot.sendMessage(chat, title + text, parse_mode="markdown")
            except TelegramError:
                try:
                    dispatcher.bot.getChat(chat)
                except Unauthorized:
                    failed += 1
                    sql.chat_leave_fed(chat)
                    LOGGER.info(
                        "Chat {} has left fed {} because I was punched".format(
                            chat,
                            fedinfo["fname"],
                        ),
                    )
                    continue
                failed += 1
                LOGGER.warning("Couldn't send broadcast to {}".format(str(chat)))

        send_text = "» ᴛʜᴇ ꜰᴇᴅᴇʀᴀᴛɪᴏɴ ʙʀᴏᴀᴅᴄᴀꜱᴛ ɪꜱ ᴄᴏᴍᴘʟᴇᴛᴇ."
        if failed >= 1:
            send_text += "» {} ᴛʜᴇ ɢʀᴏᴜᴘ ꜰᴀɪʟᴇᴅ ᴛᴏ ʀᴇᴄᴇɪᴠᴇ ᴛʜᴇ ᴍᴇꜱꜱᴀɢᴇ, ᴘʀᴏʙᴀʙʟʏ ʙᴇᴄᴀᴜꜱᴇ ɪᴛ ʟᴇꜰᴛ ᴛʜᴇ ꜰᴇᴅᴇʀᴀᴛɪᴏɴ.".format(
                failed,
            )
        update.effective_message.reply_text(send_text)


@run_async
def fed_ban_list(update: Update, context: CallbackContext):
    args, chat_data = context.args, context.chat_data
    chat = update.effective_chat
    user = update.effective_user

    if chat.type == "private":
        send_message(
            update.effective_message,
            "This command is specific to the group, not to our pm!",
        )
        return

    fed_id = sql.get_fed_id(chat.id)
    info = sql.get_fed_info(fed_id)

    if not fed_id:
        update.effective_message.reply_text(
            "» ᴛʜɪꜱ ɢʀᴏᴜᴘ ɪꜱ ɴᴏᴛ ᴀ ᴘᴀʀᴛ ᴏꜰ ᴀɴʏ ꜰᴇᴅᴇʀᴀᴛɪᴏɴ!",
        )
        return

    if is_user_fed_owner(fed_id, user.id) is False:
        update.effective_message.reply_text("Only Federation owners can do this!")
        return

    user = update.effective_user
    chat = update.effective_chat
    getfban = sql.get_all_fban_users(fed_id)
    if len(getfban) == 0:
        update.effective_message.reply_text(
            "» ᴛʜᴇ ꜰᴇᴅᴇʀᴀᴛɪᴏɴ ʙᴀɴ ʟɪꜱᴛ ᴏꜰ {} ɪꜱ ᴇᴍᴘᴛʏ!".format(info["fname"]),
            parse_mode=ParseMode.HTML,
        )
        return

    if args:
        if args[0] == "json":
            jam = time.time()
            new_jam = jam + 1800
            cek = get_chat(chat.id, chat_data)
            if cek.get("status"):
                if jam <= int(cek.get("value")):
                    waktu = time.strftime(
                        "%H:%M:%S %d/%m/%Y",
                        time.localtime(cek.get("value")),
                    )
                    update.effective_message.reply_text(
                        "» ʏᴏᴜ ᴄᴀɴ ʙᴀᴄᴋᴜᴘ ʏᴏᴜʀ ᴅᴀᴛᴀ ᴏɴᴄᴇ ᴇᴠᴇʀʏ 30 ᴍɪɴᴜᴛᴇꜱ!\n» ʏᴏᴜ ᴄᴀɴ ʙᴀᴄᴋ ᴜᴘ ᴅᴀᴛᴀ ᴀɢᴀɪɴ ᴀᴛ `{}`".format(
                            waktu,
                        ),
                        parse_mode=ParseMode.MARKDOWN,
                    )
                    return
                if user.id not in DRAGONS:
                    put_chat(chat.id, new_jam, chat_data)
            else:
                if user.id not in DRAGONS:
                    put_chat(chat.id, new_jam, chat_data)
            backups = ""
            for users in getfban:
                getuserinfo = sql.get_all_fban_users_target(fed_id, users)
                json_parser = {
                    "user_id": users,
                    "first_name": getuserinfo["first_name"],
                    "last_name": getuserinfo["last_name"],
                    "user_name": getuserinfo["user_name"],
                    "reason": getuserinfo["reason"],
                }
                backups += json.dumps(json_parser)
                backups += "\n"
            with BytesIO(str.encode(backups)) as output:
                output.name = "AltFbanUsers.json"
                update.effective_message.reply_document(
                    document=output,
                    filename="AltFbanUsers.json",
                    caption="» ᴛᴏᴛᴀʟ {} ᴜꜱᴇʀ ᴀʀᴇ ʙʟᴏᴄᴋᴇᴅ ʙʏ ᴛʜᴇ ꜰᴇᴅᴇʀᴀᴛɪᴏɴ {}.".format(
                        len(getfban),
                        info["fname"],
                    ),
                )
            return
        if args[0] == "csv":
            jam = time.time()
            new_jam = jam + 1800
            cek = get_chat(chat.id, chat_data)
            if cek.get("status"):
                if jam <= int(cek.get("value")):
                    waktu = time.strftime(
                        "%H:%M:%S %d/%m/%Y",
                        time.localtime(cek.get("value")),
                    )
                    update.effective_message.reply_text(
                        "» ʏᴏᴜ ᴄᴀɴ ʙᴀᴄᴋ ᴜᴘ ᴅᴀᴛᴀ ᴏɴᴄᴇ ᴇᴠᴇʀʏ 30 ᴍɪɴᴜᴛᴇꜱ!\n» ʏᴏᴜ ᴄᴀɴ ʙᴀᴄᴋ ᴜᴘ ᴅᴀᴛᴀ ᴀɢᴀɪɴ ᴀᴛ `{}`".format(
                            waktu,
                        ),
                        parse_mode=ParseMode.MARKDOWN,
                    )
                    return
                if user.id not in DRAGONS:
                    put_chat(chat.id, new_jam, chat_data)
            else:
                if user.id not in DRAGONS:
                    put_chat(chat.id, new_jam, chat_data)
            backups = "id,firstname,lastname,username,reason\n"
            for users in getfban:
                getuserinfo = sql.get_all_fban_users_target(fed_id, users)
                backups += (
                    "{user_id},{first_name},{last_name},{user_name},{reason}".format(
                        user_id=users,
                        first_name=getuserinfo["first_name"],
                        last_name=getuserinfo["last_name"],
                        user_name=getuserinfo["user_name"],
                        reason=getuserinfo["reason"],
                    )
                )
                backups += "\n"
            with BytesIO(str.encode(backups)) as output:
                output.name = "AltFbanUsers.csv"
                update.effective_message.reply_document(
                    document=output,
                    filename="AltFbanUsers.csv",
                    caption="» ᴛᴏᴛᴀʟ {} ᴜꜱᴇʀ ᴀʀᴇ ʙʟᴏᴄᴋᴇᴅ ʙʏ ꜰᴇᴅᴇʀᴀᴛɪᴏɴ {}.".format(
                        len(getfban),
                        info["fname"],
                    ),
                )
            return

    text = "<b>» {} ᴜꜱᴇʀꜱ ʜᴀᴠᴇ ʙᴇᴇɴ ʙᴀɴɴᴇᴅ ꜰʀᴏᴍ ᴛʜᴇ ꜰᴇᴅᴇʀᴀᴛɪᴏɴ {}:</b>\n".format(
        len(getfban),
        info["fname"],
    )
    for users in getfban:
        getuserinfo = sql.get_all_fban_users_target(fed_id, users)
        if getuserinfo is False:
            text = "» ᴛʜᴇʀᴇ ᴀʀᴇ ɴᴏ ᴜꜱᴇʀꜱ ʙᴀɴɴᴇᴅ ꜰʀᴏᴍ ᴛʜᴇ ꜰᴇᴅᴇʀᴀᴛɪᴏɴ {}".format(
                info["fname"],
            )
            break
        user_name = getuserinfo["first_name"]
        if getuserinfo["last_name"]:
            user_name += " " + getuserinfo["last_name"]
        text += " • {} (<code>{}</code>)\n".format(
            mention_html(users, user_name),
            users,
        )

    try:
        update.effective_message.reply_text(text, parse_mode=ParseMode.HTML)
    except:
        jam = time.time()
        new_jam = jam + 1800
        cek = get_chat(chat.id, chat_data)
        if cek.get("status"):
            if jam <= int(cek.get("value")):
                waktu = time.strftime(
                    "%H:%M:%S %d/%m/%Y",
                    time.localtime(cek.get("value")),
                )
                update.effective_message.reply_text(
                    "» ʏᴏᴜ ᴄᴀɴ ʙᴀᴄᴋ ᴜᴘ ᴅᴀᴛᴀ ᴏɴᴄᴇ ᴇᴠᴇʀʏ 30 ᴍɪɴᴜᴛᴇꜱ!\n» ʏᴏᴜ ᴄᴀɴ ʙᴀᴄᴋ ᴜᴘ ᴅᴀᴛᴀ ᴀɢᴀɪɴ ᴀᴛ `{}`".format(
                        waktu,
                    ),
                    parse_mode=ParseMode.MARKDOWN,
                )
                return
            if user.id not in DRAGONS:
                put_chat(chat.id, new_jam, chat_data)
        else:
            if user.id not in DRAGONS:
                put_chat(chat.id, new_jam, chat_data)
        cleanr = re.compile("<.*?>")
        cleantext = re.sub(cleanr, "", text)
        with BytesIO(str.encode(cleantext)) as output:
            output.name = "AltFbanList.txt"
            update.effective_message.reply_document(
                document=output,
                filename="AltFbanList.txt",
                caption="» ᴛʜᴇ ꜰᴏʟʟᴏᴡɪɴɢ ɪꜱ ᴀ ʟɪꜱᴛ ᴏꜰ ᴜꜱᴇʀꜱ ᴡʜᴏ ᴀʀᴇ ᴄᴜʀʀᴇɴᴛʟʏ ꜰʙᴀɴɴᴇᴅ ɪɴ ᴛʜᴇ ꜰᴇᴅᴇʀᴀᴛɪᴏɴ {}.".format(
                    info["fname"],
                ),
            )


@run_async
def fed_notif(update: Update, context: CallbackContext):
    args = context.args
    chat = update.effective_chat
    user = update.effective_user
    msg = update.effective_message
    fed_id = sql.get_fed_id(chat.id)

    if not fed_id:
        update.effective_message.reply_text(
            "This group is not a part of any federation!",
        )
        return

    if args:
        if args[0] in ("yes", "on"):
            sql.set_feds_setting(user.id, True)
            msg.reply_text(
                "Reporting Federation back up! Every user who is fban / unfban you will be notified via PM.",
            )
        elif args[0] in ("no", "off"):
            sql.set_feds_setting(user.id, False)
            msg.reply_text(
                "Reporting Federation has stopped! Every user who is fban / unfban you will not be notified via PM.",
            )
        else:
            msg.reply_text("Please enter `on`/`off`", parse_mode="markdown")
    else:
        getreport = sql.user_feds_report(user.id)
        msg.reply_text(
            "» ʏᴏᴜʀ ᴄᴜʀʀᴇɴᴛ ꜰᴇᴅᴇʀᴀᴛɪᴏɴ ʀᴇᴘᴏʀᴛ ᴘʀᴇꜰᴇʀᴇɴᴄᴇꜱ: `{}`".format(getreport),
            parse_mode="markdown",
        )


@run_async
def fed_chats(update: Update, context: CallbackContext):
    chat = update.effective_chat
    user = update.effective_user

    if chat.type == "private":
        send_message(
            update.effective_message,
            "This command is specific to the group, not to our pm!",
        )
        return

    fed_id = sql.get_fed_id(chat.id)
    info = sql.get_fed_info(fed_id)

    if not fed_id:
        update.effective_message.reply_text("» ᴛʜɪꜱ ɢʀᴏᴜᴘ ɪꜱ ɴᴏᴛ ᴀ ᴘᴀʀᴛ ᴏꜰ ᴀɴʏ ꜰᴇᴅᴇʀᴀᴛɪᴏɴ!",)
        return

    if is_user_fed_admin(fed_id, user.id) is False:
        update.effective_message.reply_text("Only federation admins can do this!")
        return

    getlist = sql.all_fed_chats(fed_id)
    if len(getlist) == 0:
        update.effective_message.reply_text(
            "» ɴᴏ ᴜꜱᴇʀꜱ ᴀʀᴇ ꜰʙᴀɴɴᴇᴅ ꜰʀᴏᴍ ᴛʜᴇ ꜰᴇᴅᴇʀᴀᴛɪᴏɴ {}".format(info["fname"]),
            parse_mode=ParseMode.HTML,
        )
        return

    text = "<b>» ɴᴇᴡ ᴄʜᴀᴛ ᴊᴏɪɴᴇᴅ ᴛʜᴇ ꜰᴇᴅᴇʀᴀᴛɪᴏɴ {}:</b>\n".format(info["fname"])
    for chats in getlist:
        try:
            chat_name = dispatcher.bot.getChat(chats).title
        except Unauthorized:
            sql.chat_leave_fed(chats)
            LOGGER.info(
                "Chat {} has leave fed {} because I was kicked".format(
                    chats,
                    info["fname"],
                ),
            )
            continue
        text += " • {} (<code>{}</code>)\n".format(chat_name, chats)

    try:
        update.effective_message.reply_text(text, parse_mode=ParseMode.HTML)
    except:
        cleanr = re.compile("<.*?>")
        cleantext = re.sub(cleanr, "", text)
        with BytesIO(str.encode(cleantext)) as output:
            output.name = "AltFedChats.txt"
            update.effective_message.reply_document(
                document=output,
                filename="AltFedChats.txt",
                caption="» ʜᴇʀᴇ ɪꜱ ᴀ ʟɪꜱᴛ ᴏꜰ ᴀʟʟ ᴛʜᴇ ᴄʜᴀᴛꜱ ᴛʜᴀᴛ ᴊᴏɪɴᴇᴅ ᴛʜᴇ ꜰᴇᴅᴇʀᴀᴛɪᴏɴ {}.".format(
                    info["fname"],
                ),
            )


@run_async
def fed_import_bans(update: Update, context: CallbackContext):
    bot, chat_data = context.bot, context.chat_data
    chat = update.effective_chat
    user = update.effective_user
    msg = update.effective_message

    if chat.type == "private":
        send_message(
            update.effective_message,
            "This command is specific to the group, not to our pm!",
        )
        return

    fed_id = sql.get_fed_id(chat.id)
    getfed = sql.get_fed_info(fed_id)

    if not fed_id:
        update.effective_message.reply_text("» ᴛʜɪꜱ ɢʀᴏᴜᴘ ɪꜱ ɴᴏᴛ ᴀ ᴘᴀʀᴛ ᴏꜰ ᴀɴʏ ꜰᴇᴅᴇʀᴀᴛɪᴏɴ!",)
        return

    if is_user_fed_owner(fed_id, user.id) is False:
        update.effective_message.reply_text("Only Federation owners can do this!")
        return

    if msg.reply_to_message and msg.reply_to_message.document:
        jam = time.time()
        new_jam = jam + 1800
        cek = get_chat(chat.id, chat_data)
        if cek.get("status"):
            if jam <= int(cek.get("value")):
                altx = time.strftime(
                    "%H:%M:%S %d/%m/%Y",
                    time.localtime(cek.get("value")),
                )
                update.effective_message.reply_text(
                    "» ʏᴏᴜ ᴄᴀɴ ɢᴇᴛ ʏᴏᴜʀ ᴅᴀᴛᴀ ᴏɴᴄᴇ ᴇᴠᴇʀʏ 30 ᴍɪɴᴜᴛᴇꜱ!\nʏᴏᴜ ᴄᴀɴ ɢᴇᴛ ᴅᴀᴛᴀ ᴀɢᴀɪɴ ᴀᴛ `{}`".format(
                        altx,
                    ),
                    parse_mode=ParseMode.MARKDOWN,
                )
                return
            if user.id not in DRAGONS:
                put_chat(chat.id, new_jam, chat_data)
        else:
            if user.id not in DRAGONS:
                put_chat(chat.id, new_jam, chat_data)
        success = 0
        failed = 0
        try:
            file_info = bot.get_file(msg.reply_to_message.document.file_id)
        except BadRequest:
            msg.reply_text(
                "Try downloading and re-uploading the file, this one seems broken!",
            )
            return
        fileformat = msg.reply_to_message.document.file_name.split(".")[-1]
        if fileformat == "json":
            multi_fed_id = []
            multi_import_userid = []
            multi_import_firstname = []
            multi_import_lastname = []
            multi_import_username = []
            multi_import_reason = []
            with BytesIO() as file:
                file_info.download(out=file)
                file.seek(0)
                reading = file.read().decode("UTF-8")
                splitting = reading.split("\n")
                for x in splitting:
                    if x == "":
                        continue
                    try:
                        data = json.loads(x)
                    except json.decoder.JSONDecodeError as err:
                        failed += 1
                        continue
                    try:
                        import_userid = int(data["user_id"])  # Make sure it int
                        import_firstname = str(data["first_name"])
                        import_lastname = str(data["last_name"])
                        import_username = str(data["user_name"])
                        import_reason = str(data["reason"])
                    except ValueError:
                        failed += 1
                        continue
                    # Checking user
                    if int(import_userid) == bot.id:
                        failed += 1
                        continue
                    if is_user_fed_owner(fed_id, import_userid) is True:
                        failed += 1
                        continue
                    if is_user_fed_admin(fed_id, import_userid) is True:
                        failed += 1
                        continue
                    if str(import_userid) == str(OWNER_ID):
                        failed += 1
                        continue
                    if int(import_userid) in DRAGONS:
                        failed += 1
                        continue
                    if int(import_userid) in TIGERS:
                        failed += 1
                        continue
                    if int(import_userid) in WOLVES:
                        failed += 1
                        continue
                    multi_fed_id.append(fed_id)
                    multi_import_userid.append(str(import_userid))
                    multi_import_firstname.append(import_firstname)
                    multi_import_lastname.append(import_lastname)
                    multi_import_username.append(import_username)
                    multi_import_reason.append(import_reason)
                    success += 1
                sql.multi_fban_user(
                    multi_fed_id,
                    multi_import_userid,
                    multi_import_firstname,
                    multi_import_lastname,
                    multi_import_username,
                    multi_import_reason,
                )
            text = "» ʙʟᴏᴄᴋꜱ ᴡᴇʀᴇ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ɪᴍᴘᴏʀᴛᴇᴅ.\n • {} ᴘᴇᴏᴘʟᴇ ᴀʀᴇ ʙʟᴏᴄᴋᴇᴅ.".format(success)
            if failed >= 1:
                text += " • {} ꜰᴀɪʟᴇᴅ ᴛᴏ ɪᴍᴘᴏʀᴛ.".format(failed)
            get_fedlog = sql.get_fed_log(fed_id)
            if get_fedlog:
                if ast.literal_eval(get_fedlog):
                    teks = "» ꜰᴇᴅ *{}* ʜᴀꜱ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ɪᴍᴘᴏʀᴛᴇᴅ ᴅᴀᴛᴀ.\n • {} ʙᴀɴɴᴇᴅ.".format(
                        getfed["fname"],
                        success,
                    )
                    if failed >= 1:
                        teks += " • {} ꜰᴀɪʟᴇᴅ ᴛᴏ ɪᴍᴘᴏʀᴛ.".format(failed)
                    bot.send_message(get_fedlog, teks, parse_mode="markdown")
        elif fileformat == "csv":
            multi_fed_id = []
            multi_import_userid = []
            multi_import_firstname = []
            multi_import_lastname = []
            multi_import_username = []
            multi_import_reason = []
            file_info.download(
                "fban_{}.csv".format(msg.reply_to_message.document.file_id),
            )
            with open(
                "fban_{}.csv".format(msg.reply_to_message.document.file_id),
                "r",
                encoding="utf8",
            ) as csvFile:
                reader = csv.reader(csvFile)
                for data in reader:
                    try:
                        import_userid = int(data[0])  # Make sure it int
                        import_firstname = str(data[1])
                        import_lastname = str(data[2])
                        import_username = str(data[3])
                        import_reason = str(data[4])
                    except ValueError:
                        failed += 1
                        continue
                    # Checking user
                    if int(import_userid) == bot.id:
                        failed += 1
                        continue
                    if is_user_fed_owner(fed_id, import_userid) is True:
                        failed += 1
                        continue
                    if is_user_fed_admin(fed_id, import_userid) is True:
                        failed += 1
                        continue
                    if str(import_userid) == str(OWNER_ID):
                        failed += 1
                        continue
                    if int(import_userid) in DRAGONS:
                        failed += 1
                        continue
                    if int(import_userid) in TIGERS:
                        failed += 1
                        continue
                    if int(import_userid) in WOLVES:
                        failed += 1
                        continue
                    multi_fed_id.append(fed_id)
                    multi_import_userid.append(str(import_userid))
                    multi_import_firstname.append(import_firstname)
                    multi_import_lastname.append(import_lastname)
                    multi_import_username.append(import_username)
                    multi_import_reason.append(import_reason)
                    success += 1
                sql.multi_fban_user(
                    multi_fed_id,
                    multi_import_userid,
                    multi_import_firstname,
                    multi_import_lastname,
                    multi_import_username,
                    multi_import_reason,
                )
            csvFile.close()
            os.remove("fban_{}.csv".format(msg.reply_to_message.document.file_id))
            text = "» ꜰɪʟᴇꜱ ᴡᴇʀᴇ ɪᴍᴘᴏʀᴛᴇᴅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ.\n • {} ᴘᴇᴏᴘʟᴇ ʙᴀɴɴᴇᴅ.".format(success)
            if failed >= 1:
                text += " • {} Failed to import.".format(failed)
            get_fedlog = sql.get_fed_log(fed_id)
            if get_fedlog:
                if ast.literal_eval(get_fedlog):
                    teks = "» ꜰᴇᴅ *{}* ʜᴀꜱ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ɪᴍᴘᴏʀᴛᴇᴅ ᴅᴀᴛᴀ.\n • {} ʙᴀɴɴᴇᴅ.".format(
                        getfed["fname"],
                        success,
                    )
                    if failed >= 1:
                        teks += " • {} ꜰᴀɪʟᴇᴅ ᴛᴏ ɪᴍᴘᴏʀᴛ.".format(failed)
                    bot.send_message(get_fedlog, teks, parse_mode="markdown")
        else:
            send_message(update.effective_message, "This file is not supported.")
            return
        send_message(update.effective_message, text)


@run_async
def del_fed_button(update: Update, context: CallbackContext):
    query = update.callback_query
    fed_id = query.data.split("_")[1]

    if fed_id == "cancel":
        query.message.edit_text("» ꜰᴇᴅᴇʀᴀᴛɪᴏɴ ᴅᴇʟᴇᴛɪᴏɴ ᴄᴀɴᴄᴇʟʟᴇᴅ!")
        return

    getfed = sql.get_fed_info(fed_id)
    if getfed:
        delete = sql.del_fed(fed_id)
        if delete:
            query.message.edit_text(
                "» ʏᴏᴜ ʜᴀᴠᴇ ʀᴇᴍᴏᴠᴇᴅ ʏᴏᴜʀ ꜰᴇᴅᴇʀᴀᴛɪᴏɴ!\n» ɴᴏᴡ ᴀʟʟ ᴛʜᴇ ɢʀᴏᴜᴘꜱ ᴛʜᴀᴛ ᴀʀᴇ ᴄᴏɴɴᴇᴄᴛᴇᴅ ᴡɪᴛʜ `{}` ᴅᴏ ɴᴏᴛ ʜᴀᴠᴇ ᴀ ꜰᴇᴅᴇʀᴀᴛɪᴏɴ.".format(
                    getfed["fname"],
                ),
                parse_mode="markdown",
            )


@run_async
def fed_stat_user(update: Update, context: CallbackContext):
    bot, args = context.bot, context.args
    msg = update.effective_message

    if args:
        if args[0].isdigit():
            user_id = args[0]
        else:
            user_id = extract_user(msg, args)
    else:
        user_id = extract_user(msg, args)

    if user_id:
        if len(args) == 2 and args[0].isdigit():
            fed_id = args[1]
            user_name, reason, fbantime = sql.get_user_fban(fed_id, str(user_id))
            if fbantime:
                fbantime = time.strftime("%d/%m/%Y", time.localtime(fbantime))
            else:
                fbantime = "ᴜɴᴀᴠᴀɪᴀʙʟᴇ"
            if user_name is False:
                send_message(
                    update.effective_message,
                    "» ꜰᴇᴅ {} ɴᴏᴛ ꜰᴏᴜɴᴅ!".format(fed_id),
                    parse_mode="markdown",
                )
                return
            if user_name == "" or user_name is None:
                user_name = "ʜᴇ/ꜱʜᴇ"
            if not reason:
                send_message(
                    update.effective_message,
                    "» {} ɪꜱ ɴᴏᴛ ʙᴀɴɴᴇᴅ ɪɴ ᴛʜɪꜱ ꜰᴇᴅᴇʀᴀᴛɪᴏɴ!".format(user_name),
                )
            else:
                teks = "» {} ʙᴀɴɴᴇᴅ ɪɴ ᴛʜɪꜱ ꜰᴇᴅᴇʀᴀᴛɪᴏɴ ʙᴇᴄᴀᴜꜱᴇ:\n`{}`\n» *ʙᴀɴɴᴇᴅ ᴀᴛ:* `{}`".format(
                    user_name,
                    reason,
                    fbantime,
                )
                send_message(update.effective_message, teks, parse_mode="markdown")
            return
        user_name, fbanlist = sql.get_user_fbanlist(str(user_id))
        if user_name == "":
            try:
                user_name = bot.get_chat(user_id).first_name
            except BadRequest:
                user_name = "ʜᴇ/ꜱʜᴇ"
            if user_name == "" or user_name is None:
                user_name = "ʜᴇ/ꜱʜᴇ"
        if len(fbanlist) == 0:
            send_message(
                update.effective_message,
                "» {} ɪꜱ ɴᴏᴛ ʙᴀɴɴᴇᴅ ɪɴ ᴀɴʏ ꜰᴇᴅᴇʀᴀᴛɪᴏɴ!".format(user_name),
            )
            return
        teks = "» {} ʜᴀꜱ ʙᴇᴇɴ ʙᴀɴɴᴇᴅ ɪɴ ᴛʜɪꜱ ꜰᴇᴅᴇʀᴀᴛɪᴏɴ:\n".format(user_name)
        for x in fbanlist:
            teks += "- `{}`: {}\n".format(x[0], x[1][:20])
        teks += "\n\n‣ ɪꜰ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ꜰɪɴᴅ ᴏᴜᴛ ᴍᴏʀᴇ ᴀʙᴏᴜᴛ ᴛʜᴇ ʀᴇᴀꜱᴏɴꜱ ꜰᴏʀ ꜰᴇᴅʙᴀɴ ꜱᴘᴇᴄɪꜰɪᴄᴀʟʟʏ, ᴜꜱᴇ /fstat <ꜰᴇᴅ-ɪᴅ>"
        send_message(update.effective_message, teks, parse_mode="markdown")

    elif not msg.reply_to_message and not args:
        user_id = msg.from_user.id
        user_name, fbanlist = sql.get_user_fbanlist(user_id)
        if user_name == "":
            user_name = msg.from_user.first_name
        if len(fbanlist) == 0:
            send_message(
                update.effective_message,
                "» {} ɪꜱ ɴᴏᴛ ʙᴀɴɴᴇᴅ ɪɴ ᴀɴʏ ꜰᴇᴅᴇʀᴀᴛɪᴏɴ!".format(user_name),
            )
        else:
            teks = "» {} ʜᴀꜱ ʙᴇᴇɴ ʙᴀɴɴᴇᴅ ɪɴ ᴛʜɪꜱ ꜰᴇᴅᴇʀᴀᴛɪᴏɴ:\n".format(user_name)
            for x in fbanlist:
                teks += "- `{}`: {}\n".format(x[0], x[1][:20])
            teks += "\n‣ ɪꜰ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ꜰɪɴᴅ ᴏᴜᴛ ᴍᴏʀᴇ ᴀʙᴏᴜᴛ ᴛʜᴇ ʀᴇᴀꜱᴏɴꜱ ꜰᴏʀ ꜰᴇᴅʙᴀɴ ꜱᴘᴇᴄɪꜰɪᴄᴀʟʟʏ, ᴜꜱᴇ /fstat <ꜰᴇᴅ-ɪᴅ>"
            send_message(update.effective_message, teks, parse_mode="markdown")

    else:
        fed_id = args[0]
        fedinfo = sql.get_fed_info(fed_id)
        if not fedinfo:
            send_message(update.effective_message, "» ꜰᴇᴅ {} ɴᴏᴛ ꜰᴏᴜɴᴅ!".format(fed_id))
            return
        name, reason, fbantime = sql.get_user_fban(fed_id, msg.from_user.id)
        if fbantime:
            fbantime = time.strftime("%d/%m/%Y", time.localtime(fbantime))
        else:
            fbantime = "ᴜɴᴀᴠᴀɪᴀʙʟᴇ"
        if not name:
            name = msg.from_user.first_name
        if not reason:
            send_message(
                update.effective_message,
                "» {} ɪꜱ ɴᴏᴛ ʙᴀɴɴᴇᴅ ɪɴ ᴛʜɪꜱ ꜰᴇᴅᴇʀᴀᴛɪᴏɴ.".format(name),
            )
            return
        send_message(
            update.effective_message,
            "» {} ʙᴀɴɴᴇᴅ ɪɴ ᴛʜɪꜱ ꜰᴇᴅᴇʀᴀᴛɪᴏɴ ʙᴇᴄᴀᴜꜱᴇ:\n`{}`\n» *ʙᴀɴɴᴇᴅ ᴀᴛ:* `{}`".format(
                name,
                reason,
                fbantime,
            ),
            parse_mode="markdown",
        )


@run_async
def set_fed_log(update: Update, context: CallbackContext):
    args = context.args
    chat = update.effective_chat
    user = update.effective_user

    if chat.type == "private":
        send_message(
            update.effective_message,
            "This command is specific to the group, not to our pm!",
        )
        return

    if args:
        fedinfo = sql.get_fed_info(args[0])
        if not fedinfo:
            send_message(update.effective_message, "This Federation does not exist!")
            return
        isowner = is_user_fed_owner(args[0], user.id)
        if not isowner:
            send_message(
                update.effective_message,
                "Only federation creator can set federation logs.",
            )
            return
        setlog = sql.set_fed_log(args[0], chat.id)
        if setlog:
            send_message(
                update.effective_message,
                "» ꜰᴇᴅᴇʀᴀᴛɪᴏɴ ʟᴏɢ `{}` ʜᴀꜱ ʙᴇᴇɴ ꜱᴇᴛ ᴛᴏ {}".format(
                    fedinfo["fname"],
                    chat.title,
                ),
                parse_mode="markdown",
            )
    else:
        send_message(
            update.effective_message,
            "You have not provided your federated ID!",
        )


@run_async
def unset_fed_log(update: Update, context: CallbackContext):
    args = context.args
    chat = update.effective_chat
    user = update.effective_user

    if chat.type == "private":
        send_message(
            update.effective_message,
            "This command is specific to the group, not to our pm!",
        )
        return

    if args:
        fedinfo = sql.get_fed_info(args[0])
        if not fedinfo:
            send_message(update.effective_message, "This Federation does not exist!")
            return
        isowner = is_user_fed_owner(args[0], user.id)
        if not isowner:
            send_message(
                update.effective_message,
                "Only federation creator can set federation logs.",
            )
            return
        setlog = sql.set_fed_log(args[0], None)
        if setlog:
            send_message(
                update.effective_message,
                "» ꜰᴇᴅᴇʀᴀᴛɪᴏɴ ʟᴏɢ `{}` ʜᴀꜱ ʙᴇᴇɴ ʀᴇᴠᴏᴋᴇᴅ ᴏɴ {}".format(
                    fedinfo["fname"],
                    chat.title,
                ),
                parse_mode="markdown",
            )
    else:
        send_message(
            update.effective_message,
            "You have not provided your federated ID!",
        )


@run_async
def subs_feds(update: Update, context: CallbackContext):
    bot, args = context.bot, context.args
    chat = update.effective_chat
    user = update.effective_user

    if chat.type == "private":
        send_message(
            update.effective_message,
            "This command is specific to the group, not to our pm!",
        )
        return

    fed_id = sql.get_fed_id(chat.id)
    fedinfo = sql.get_fed_info(fed_id)

    if not fed_id:
        send_message(update.effective_message, "» ᴛʜɪꜱ ɢʀᴏᴜᴘ ɪꜱ ɴᴏᴛ ɪɴ ᴀɴʏ ꜰᴇᴅᴇʀᴀᴛɪᴏɴ!")
        return

    if is_user_fed_owner(fed_id, user.id) is False:
        send_message(update.effective_message, "Only fed owner can do this!")
        return

    if args:
        getfed = sql.search_fed_by_id(args[0])
        if getfed is False:
            send_message(
                update.effective_message,
                "Please enter a valid federation id.",
            )
            return
        subfed = sql.subs_fed(args[0], fed_id)
        if subfed:
            send_message(
                update.effective_message,
                "Federation `{}` has subscribe the federation `{}`. Every time there is a Fedban from that federation, this federation will also banned that user.".format(
                    fedinfo["fname"],
                    getfed["fname"],
                ),
                parse_mode="markdown",
            )
            get_fedlog = sql.get_fed_log(args[0])
            if get_fedlog:
                if int(get_fedlog) != int(chat.id):
                    bot.send_message(
                        get_fedlog,
                        "Federation `{}` has subscribe the federation `{}`".format(
                            fedinfo["fname"],
                            getfed["fname"],
                        ),
                        parse_mode="markdown",
                    )
        else:
            send_message(
                update.effective_message,
                "Federation `{}` already subscribe the federation `{}`.".format(
                    fedinfo["fname"],
                    getfed["fname"],
                ),
                parse_mode="markdown",
            )
    else:
        send_message(
            update.effective_message,
            "You have not provided your federated ID!",
        )


@run_async
def unsubs_feds(update: Update, context: CallbackContext):
    bot, args = context.bot, context.args
    chat = update.effective_chat
    user = update.effective_user

    if chat.type == "private":
        send_message(
            update.effective_message,
            "This command is specific to the group, not to our pm!",
        )
        return

    fed_id = sql.get_fed_id(chat.id)
    fedinfo = sql.get_fed_info(fed_id)

    if not fed_id:
        send_message(update.effective_message, "» ᴛʜɪꜱ ɢʀᴏᴜᴘ ɪꜱ ɴᴏᴛ ɪɴ ᴀɴʏ ꜰᴇᴅᴇʀᴀᴛɪᴏɴ!")
        return

    if is_user_fed_owner(fed_id, user.id) is False:
        send_message(update.effective_message, "Only fed owner can do this!")
        return

    if args:
        getfed = sql.search_fed_by_id(args[0])
        if getfed is False:
            send_message(
                update.effective_message,
                "Please enter a valid federation id.",
            )
            return
        subfed = sql.unsubs_fed(args[0], fed_id)
        if subfed:
            send_message(
                update.effective_message,
                "Federation `{}` now unsubscribe fed `{}`.".format(
                    fedinfo["fname"],
                    getfed["fname"],
                ),
                parse_mode="markdown",
            )
            get_fedlog = sql.get_fed_log(args[0])
            if get_fedlog:
                if int(get_fedlog) != int(chat.id):
                    bot.send_message(
                        get_fedlog,
                        "Federation `{}` has unsubscribe fed `{}`.".format(
                            fedinfo["fname"],
                            getfed["fname"],
                        ),
                        parse_mode="markdown",
                    )
        else:
            send_message(
                update.effective_message,
                "Federation `{}` is not subscribing `{}`.".format(
                    fedinfo["fname"],
                    getfed["fname"],
                ),
                parse_mode="markdown",
            )
    else:
        send_message(
            update.effective_message,
            "You have not provided your federated ID!",
        )


@run_async
def get_myfedsubs(update: Update, context: CallbackContext):
    chat = update.effective_chat
    user = update.effective_user

    if chat.type == "private":
        send_message(
            update.effective_message,
            "This command is specific to the group, not to our pm!",
        )
        return

    fed_id = sql.get_fed_id(chat.id)
    fedinfo = sql.get_fed_info(fed_id)

    if not fed_id:
        send_message(update.effective_message, "» ᴛʜɪꜱ ɢʀᴏᴜᴘ ɪꜱ ɴᴏᴛ ɪɴ ᴀɴʏ ꜰᴇᴅᴇʀᴀᴛɪᴏɴ!")
        return

    if is_user_fed_owner(fed_id, user.id) is False:
        send_message(update.effective_message, "Only fed owner can do this!")
        return

    try:
        getmy = sql.get_mysubs(fed_id)
    except:
        getmy = []

    if len(getmy) == 0:
        send_message(
            update.effective_message,
            "Federation `{}` is not subscribing any federation.".format(
                fedinfo["fname"],
            ),
            parse_mode="markdown",
        )
        return
    listfed = "Federation `{}` is subscribing federation:\n".format(
        fedinfo["fname"],
    )
    for x in getmy:
        listfed += "- `{}`\n".format(x)
    listfed += (
        "\n‣ To get fed info `/fedinfo <fedid>`. To unsubscribe `/unsubfed <fedid>`."
    )
    send_message(update.effective_message, listfed, parse_mode="markdown")


@run_async
def get_myfeds_list(update: Update, context: CallbackContext):
    user = update.effective_user

    fedowner = sql.get_user_owner_fed_full(user.id)
    if fedowner:
        text = "» *You are owner of feds:\n*"
        for f in fedowner:
            text += " • `{}`: *{}*\n".format(f["fed_id"], f["fed"]["fname"])
    else:
        text = "» *ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ʜᴀᴠᴇ ᴀɴʏ ꜰᴇᴅꜱ!*"
    send_message(update.effective_message, text, parse_mode="markdown")


def is_user_fed_admin(fed_id, user_id):
    fed_admins = sql.all_fed_users(fed_id)
    if fed_admins is False:
        return False
    return bool(int(user_id) in fed_admins or int(user_id) == OWNER_ID)


def is_user_fed_owner(fed_id, user_id):
    getsql = sql.get_fed_info(fed_id)
    if getsql is False:
        return False
    getfedowner = ast.literal_eval(getsql["fusers"])
    if getfedowner is None or getfedowner is False:
        return False
    getfedowner = getfedowner["owner"]
    return bool(str(user_id) == getfedowner or int(user_id) == OWNER_ID)


# There's no handler for this yet, but updating for v12 in case its used
def welcome_fed(update: Update, context: CallbackContext):
    bot = context.bot
    chat = update.effective_chat
    user = update.effective_user
    fed_id = sql.get_fed_id(chat.id)
    fban, fbanreason, fbantime = sql.get_fban_user(fed_id, user.id)
    if fban:
        update.effective_message.reply_text(
            "» ᴛʜɪꜱ ᴜꜱᴇʀ ɪꜱ ʙᴀɴɴᴇᴅ ɪɴ ᴄᴜʀʀᴇɴᴛ ꜰᴇᴅᴇʀᴀᴛɪᴏɴ! ɪ ᴡɪʟʟ ʀᴇᴍᴏᴠᴇ ʜɪᴍ.",
        )
        bot.kick_chat_member(chat.id, user.id)
        return True
    return False


def __stats__():
    all_fbanned = sql.get_all_fban_users_global()
    all_feds = sql.get_all_feds_users_global()
    return "• {} ʙᴀɴɴᴇᴅ ᴜꜱᴇʀꜱ, ᴀᴄʀᴏꜱꜱ {} ꜰᴇᴅᴇʀᴀᴛɪᴏɴꜱ".format(
        len(all_fbanned),
        len(all_feds),
    )


def __user_info__(user_id, chat_id):
    fed_id = sql.get_fed_id(chat_id)
    if fed_id:
        fban, fbanreason, fbantime = sql.get_fban_user(fed_id, user_id)
        info = sql.get_fed_info(fed_id)
        infoname = info["fname"]

        if int(info["owner"]) == user_id:
            text = "Federation owner of: <b>{}</b>.".format(infoname)
        elif is_user_fed_admin(fed_id, user_id):
            text = "Federation admin of: <b>{}</b>.".format(infoname)

        elif fban:
            text = "Federation banned: <b>Yes</b>"
            text += "\n<b>Reason:</b> {}".format(fbanreason)
        else:
            text = "Federation banned: <b>No</b>"
    else:
        text = ""
    return text


# Temporary data
def put_chat(chat_id, value, chat_data):
    if value is False:
        status = False
    else:
        status = True
    chat_data[chat_id] = {"federation": {"status": status, "value": value}}


def get_chat(chat_id, chat_data):
    try:
        value = chat_data[chat_id]["federation"]
        return value
    except KeyError:
        return {"status": False, "value": False}


__mod_name__ = "Fᴇᴅs"
__help__ = """
‣ ᴀʜ, ɢʀᴏᴜᴘ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ. ɪᴛ'ꜱ ᴀʟʟ ꜰᴜɴ ᴀɴᴅ ɢᴀᴍᴇꜱ, ᴜɴᴛɪʟ ʏᴏᴜ ꜱᴛᴀʀᴛ ɢᴇᴛᴛɪɴɢ ꜱᴘᴀᴍᴍᴇʀꜱ ɪɴ, ᴀɴᴅ ʏᴏᴜ ɴᴇᴇᴅ ᴛᴏ ʙᴀɴ ᴛʜᴇᴍ. ᴛʜᴇɴ ʏᴏᴜ ɴᴇᴇᴅ ᴛᴏ ꜱᴛᴀʀᴛ ʙᴀɴɴɪɴɢ ᴍᴏʀᴇ, ᴀɴᴅ ᴍᴏʀᴇ, ᴀɴᴅ ɪᴛ ɢᴇᴛꜱ ᴘᴀɪɴꜰᴜʟ.
‣ ʙᴜᴛ ᴛʜᴇɴ ʏᴏᴜ ʜᴀᴠᴇ ᴍᴜʟᴛɪᴘʟᴇ ɢʀᴏᴜᴘꜱ, ᴀɴᴅ ʏᴏᴜ ᴅᴏɴ'ᴛ ᴡᴀɴᴛ ᴛʜᴇꜱᴇ ꜱᴘᴀᴍᴍᴇʀꜱ ɪɴ ᴀɴʏ ᴏꜰ ʏᴏᴜʀ ɢʀᴏᴜᴘꜱ - ʜᴏᴡ ᴄᴀɴ ʏᴏᴜ ᴅᴇᴀʟ? ᴅᴏ ʏᴏᴜ ʜᴀᴠᴇ ᴛᴏ ʙᴀɴ ᴛʜᴇᴍ ᴍᴀɴᴜᴀʟʟʏ, ɪɴ ᴀʟʟ ʏᴏᴜʀ ɢʀᴏᴜᴘꜱ?

‣ ɴᴏ ᴍᴏʀᴇ! ᴡɪᴛʜ ꜰᴇᴅᴇʀᴀᴛɪᴏɴꜱ, ʏᴏᴜ ᴄᴀɴ ᴍᴀᴋᴇ ᴀ ʙᴀɴ ɪɴ ᴏɴᴇ ᴄʜᴀᴛ ᴏᴠᴇʀʟᴀᴘ ᴛᴏ ᴀʟʟ ʏᴏᴜʀ ᴏᴛʜᴇʀ ᴄʜᴀᴛꜱ.
‣ ʏᴏᴜ ᴄᴀɴ ᴇᴠᴇɴ ᴀᴘᴘᴏɪɴᴛ ꜰᴇᴅᴇʀᴀᴛɪᴏɴ ᴀᴅᴍɪɴꜱ, ꜱᴏ ᴛʜᴀᴛ ʏᴏᴜʀ ᴛʀᴜꜱᴛᴡᴏʀᴛʜɪᴇꜱᴛ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ʙᴀɴ ᴀᴄʀᴏꜱꜱ ᴀʟʟ ᴛʜᴇ ᴄʜᴀᴛꜱ ᴛʜᴀᴛ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴘʀᴏᴛᴇᴄᴛ.
"""


NEW_FED_HANDLER = CommandHandler("newfed", new_fed)
DEL_FED_HANDLER = CommandHandler("delfed", del_fed)
RENAME_FED = CommandHandler("renamefed", rename_fed)
JOIN_FED_HANDLER = CommandHandler("joinfed", join_fed)
LEAVE_FED_HANDLER = CommandHandler("leavefed", leave_fed)
PROMOTE_FED_HANDLER = CommandHandler("fpromote", user_join_fed)
DEMOTE_FED_HANDLER = CommandHandler("fdemote", user_demote_fed)
INFO_FED_HANDLER = CommandHandler("fedinfo", fed_info)
BAN_FED_HANDLER = DisableAbleCommandHandler("fban", fed_ban)
UN_BAN_FED_HANDLER = CommandHandler("unfban", unfban)
FED_BROADCAST_HANDLER = CommandHandler("fbroadcast", fed_broadcast)
FED_SET_RULES_HANDLER = CommandHandler("setfrules", set_frules)
FED_GET_RULES_HANDLER = CommandHandler("frules", get_frules)
FED_CHAT_HANDLER = CommandHandler("chatfed", fed_chat)
FED_ADMIN_HANDLER = CommandHandler("fedadmins", fed_admin)
FED_USERBAN_HANDLER = CommandHandler("fbanlist", fed_ban_list)
FED_NOTIF_HANDLER = CommandHandler("fednotif", fed_notif)
FED_CHATLIST_HANDLER = CommandHandler("fedchats", fed_chats)
FED_IMPORTBAN_HANDLER = CommandHandler("importfbans", fed_import_bans)
FEDSTAT_USER = DisableAbleCommandHandler(["fedstat", "fbanstat", "fstat"], fed_stat_user)
SET_FED_LOG = CommandHandler("setfedlog", set_fed_log)
UNSET_FED_LOG = CommandHandler("unsetfedlog", unset_fed_log)
SUBS_FED = CommandHandler("subfed", subs_feds)
UNSUBS_FED = CommandHandler("unsubfed", unsubs_feds)
MY_SUB_FED = CommandHandler("fedsubs", get_myfedsubs)
MY_FEDS_LIST = CommandHandler("myfeds", get_myfeds_list)
DELETEBTN_FED_HANDLER = CallbackQueryHandler(del_fed_button, pattern=r"rmfed_")

dispatcher.add_handler(NEW_FED_HANDLER)
dispatcher.add_handler(DEL_FED_HANDLER)
dispatcher.add_handler(RENAME_FED)
dispatcher.add_handler(JOIN_FED_HANDLER)
dispatcher.add_handler(LEAVE_FED_HANDLER)
dispatcher.add_handler(PROMOTE_FED_HANDLER)
dispatcher.add_handler(DEMOTE_FED_HANDLER)
dispatcher.add_handler(INFO_FED_HANDLER)
dispatcher.add_handler(BAN_FED_HANDLER)
dispatcher.add_handler(UN_BAN_FED_HANDLER)
dispatcher.add_handler(FED_BROADCAST_HANDLER)
dispatcher.add_handler(FED_SET_RULES_HANDLER)
dispatcher.add_handler(FED_GET_RULES_HANDLER)
dispatcher.add_handler(FED_CHAT_HANDLER)
dispatcher.add_handler(FED_ADMIN_HANDLER)
dispatcher.add_handler(FED_USERBAN_HANDLER)
dispatcher.add_handler(FED_NOTIF_HANDLER)
dispatcher.add_handler(FED_CHATLIST_HANDLER)
dispatcher.add_handler(FED_IMPORTBAN_HANDLER)
dispatcher.add_handler(FEDSTAT_USER)
dispatcher.add_handler(SET_FED_LOG)
dispatcher.add_handler(UNSET_FED_LOG)
dispatcher.add_handler(SUBS_FED)
dispatcher.add_handler(UNSUBS_FED)
dispatcher.add_handler(MY_SUB_FED)
dispatcher.add_handler(MY_FEDS_LIST)
dispatcher.add_handler(DELETEBTN_FED_HANDLER)
