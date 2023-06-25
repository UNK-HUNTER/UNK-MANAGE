import html

from telegram import ChatPermissions, ParseMode, Update
from telegram.error import BadRequest
from telegram.ext import CallbackContext, CommandHandler, Filters, MessageHandler
from telegram.ext.dispatcher import run_async
from telegram.utils.helpers import mention_markdown

import AltronRobot.modules.sql.blsticker_sql as sql
from AltronRobot import LOGGER, dispatcher
from AltronRobot.modules.connection import connected
from AltronRobot.modules.disable import DisableAbleCommandHandler
from AltronRobot.modules.helper_funcs.alternate import send_message
from AltronRobot.modules.helper_funcs.chat_status import user_admin, user_not_admin
from AltronRobot.modules.helper_funcs.misc import split_message
from AltronRobot.modules.helper_funcs.string_handling import extract_time
from AltronRobot.modules.channel import loggable
from AltronRobot.modules.warns import warn


@run_async
def blackliststicker(update: Update, context: CallbackContext):
    chat = update.effective_chat
    user = update.effective_user
    bot, args = context.bot, context.args
    conn = connected(bot, update, chat, user.id, need_admin=False)
    if conn:
        chat_id = conn
        chat_name = dispatcher.bot.getChat(conn).title
    else:
        if chat.type == "private":
            return
        chat_id = update.effective_chat.id
        chat_name = chat.title

    sticker_list = "<b>» ʟɪꜱᴛ ʙʟᴀᴄᴋʟɪꜱᴛᴇᴅ ꜱᴛɪᴄᴋᴇʀꜱ ᴄᴜʀʀᴇɴᴛʟʏ ɪɴ {}:</b>\n\n".format(chat_name)

    all_stickerlist = sql.get_chat_stickers(chat_id)

    if len(args) > 0 and args[0].lower() == "copy":
        for trigger in all_stickerlist:
            sticker_list += "<code>{}</code>\n".format(html.escape(trigger))
    elif len(args) == 0:
        for trigger in all_stickerlist:
            sticker_list += " - <code>{}</code>\n".format(html.escape(trigger))

    split_text = split_message(sticker_list)
    for text in split_text:
        if sticker_list == "<b>» ʟɪꜱᴛ ʙʟᴀᴄᴋʟɪꜱᴛᴇᴅ ꜱᴛɪᴄᴋᴇʀꜱ ᴄᴜʀʀᴇɴᴛʟʏ ɪɴ {}:</b>\n\n".format(
            chat_name
        ).format(html.escape(chat_name)):
            send_message(
                update.effective_message,
                "» ᴛʜᴇʀᴇ ᴀʀᴇ ɴᴏ ʙʟᴀᴄᴋʟɪꜱᴛ ꜱᴛɪᴄᴋᴇʀꜱ ɪɴ <b>{}</b>!".format(
                    html.escape(chat_name)
                ),
                parse_mode=ParseMode.HTML,
            )
            return
    send_message(update.effective_message, text, parse_mode=ParseMode.HTML)


@run_async
@user_admin
def add_blackliststicker(update: Update, context: CallbackContext):
    bot = context.bot
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    words = msg.text.split(None, 1)
    bot = context.bot
    conn = connected(bot, update, chat, user.id)
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
        text = words[1].replace("https://t.me/addstickers/", "")
        to_blacklist = list(
            {trigger.strip() for trigger in text.split("\n") if trigger.strip()}
        )

        added = 0
        for trigger in to_blacklist:
            try:
                bot.getStickerSet(trigger)
                sql.add_to_stickers(chat_id, trigger.lower())
                added += 1
            except BadRequest:
                send_message(
                    update.effective_message,
                    "Sticker `{}` can not be found!".format(trigger),
                    parse_mode="markdown",
                )

        if added == 0:
            return

        if len(to_blacklist) == 1:
            send_message(
                update.effective_message,
                "» ꜱᴛɪᴄᴋᴇʀ <code>{}</code> ᴀᴅᴅᴇᴅ ᴛᴏ ʙʟᴀᴄᴋʟɪꜱᴛ ꜱᴛɪᴄᴋᴇʀꜱ ɪɴ <b>{}</b>!".format(
                    html.escape(to_blacklist[0]), html.escape(chat_name)
                ),
                parse_mode=ParseMode.HTML,
            )
        else:
            send_message(
                update.effective_message,
                "» <code>{}</code> ꜱᴛɪᴄᴋᴇʀꜱ ᴀᴅᴅᴇᴅ ᴛᴏ ʙʟᴀᴄᴋʟɪꜱᴛ ꜱᴛɪᴄᴋᴇʀ ɪɴ <b>{}</b>!".format(
                    added, html.escape(chat_name)
                ),
                parse_mode=ParseMode.HTML,
            )
    elif msg.reply_to_message:
        added = 0
        trigger = msg.reply_to_message.sticker.set_name
        if trigger is None:
            send_message(update.effective_message, "Sticker is invalid!")
            return
        try:
            bot.getStickerSet(trigger)
            sql.add_to_stickers(chat_id, trigger.lower())
            added += 1
        except BadRequest:
            send_message(
                update.effective_message,
                "Sticker `{}` can not be found!".format(trigger),
                parse_mode="markdown",
            )

        if added == 0:
            return

        send_message(
            update.effective_message,
            "» ꜱᴛɪᴄᴋᴇʀ <code>{}</code> ᴀᴅᴅᴇᴅ ᴛᴏ ʙʟᴀᴄᴋʟɪꜱᴛ ꜱᴛɪᴄᴋᴇʀꜱ ɪɴ <b>{}</b>!".format(
                trigger, html.escape(chat_name)
            ),
            parse_mode=ParseMode.HTML,
        )
    else:
        send_message(
            update.effective_message,
            "Tell me what stickers you want to add to the blacklist.",
        )


@run_async
@user_admin
def unblackliststicker(update: Update, context: CallbackContext):
    bot = context.bot
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    words = msg.text.split(None, 1)
    bot = context.bot
    conn = connected(bot, update, chat, user.id)
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
        text = words[1].replace("https://t.me/addstickers/", "")
        to_unblacklist = list(
            {trigger.strip() for trigger in text.split("\n") if trigger.strip()}
        )

        successful = 0
        for trigger in to_unblacklist:
            success = sql.rm_from_stickers(chat_id, trigger.lower())
            if success:
                successful += 1

        if len(to_unblacklist) == 1:
            if successful:
                send_message(
                    update.effective_message,
                    "» ꜱᴛɪᴄᴋᴇʀ <code>{}</code> ᴅᴇʟᴇᴛᴇᴅ ꜰʀᴏᴍ ʙʟᴀᴄᴋʟɪꜱᴛ ɪɴ <b>{}</b>!".format(
                        html.escape(to_unblacklist[0]), html.escape(chat_name)
                    ),
                    parse_mode=ParseMode.HTML,
                )
            else:
                send_message(
                    update.effective_message, "This sticker is not on the blacklist...!"
                )

        elif successful == len(to_unblacklist):
            send_message(
                update.effective_message,
                "» ꜱᴛɪᴄᴋᴇʀ <code>{}</code> ᴅᴇʟᴇᴛᴇᴅ ꜰʀᴏᴍ ʙʟᴀᴄᴋʟɪꜱᴛ ɪɴ <b>{}</b>!".format(
                    successful, html.escape(chat_name)
                ),
                parse_mode=ParseMode.HTML,
            )

        elif not successful:
            send_message(
                update.effective_message,
                "None of these stickers exist, so they cannot be removed.",
                parse_mode=ParseMode.HTML,
            )

        else:
            send_message(
                update.effective_message,
                "» ꜱᴛɪᴄᴋᴇʀ <code>{}</code> ᴅᴇʟᴇᴛᴇᴅ ꜰʀᴏᴍ ʙʟᴀᴄᴋʟɪꜱᴛ.\n» {} ᴅɪᴅ ɴᴏᴛ ᴇxɪꜱᴛ, ꜱᴏ ɪᴛ'ꜱ ɴᴏᴛ ᴅᴇʟᴇᴛᴇᴅ.".format(
                    successful, len(to_unblacklist) - successful
                ),
                parse_mode=ParseMode.HTML,
            )
    elif msg.reply_to_message:
        trigger = msg.reply_to_message.sticker.set_name
        if trigger is None:
            send_message(update.effective_message, "Sticker is invalid!")
            return
        success = sql.rm_from_stickers(chat_id, trigger.lower())

        if success:
            send_message(
                update.effective_message,
                "» ꜱᴛɪᴄᴋᴇʀ <code>{}</code> ᴅᴇʟᴇᴛᴇᴅ ꜰʀᴏᴍ ʙʟᴀᴄᴋʟɪꜱᴛ ɪɴ <b>{}</b>!".format(
                    trigger, chat_name
                ),
                parse_mode=ParseMode.HTML,
            )
        else:
            send_message(
                update.effective_message,
                "» {} ɴᴏᴛ ꜰᴏᴜɴᴅ ᴏɴ ʙʟᴀᴄᴋʟɪꜱᴛᴇᴅ ꜱᴛɪᴄᴋᴇʀꜱ...!".format(trigger),
            )
    else:
        send_message(
            update.effective_message,
            "Tell me what stickers you want to add to the blacklist.",
        )


@run_async
@loggable
@user_admin
def blacklist_mode(update: Update, context: CallbackContext):
    chat = update.effective_chat
    user = update.effective_user
    bot, args = context.bot, context.args
    conn = connected(bot, update, chat, user.id, need_admin=True)
    if conn:
        chat = dispatcher.bot.getChat(conn)
        chat_id = conn
        chat_name = dispatcher.bot.getChat(conn).title
    else:
        if update.effective_message.chat.type == "private":
            send_message(update.effective_message, "You can do this command in groups, not in PM")
            return ""
        chat = update.effective_chat
        chat_id = update.effective_chat.id
        chat_name = update.effective_message.chat.title

    if args:
        if args[0].lower() in ["off", "nothing", "no"]:
            settypeblacklist = "ᴛᴜʀɴ ᴏꜰꜰ"
            sql.set_blacklist_strength(chat_id, 0, "0")
        elif args[0].lower() in ["del", "delete"]:
            settypeblacklist = "ʟᴇꜰᴛ, ᴛʜᴇ ᴍᴇꜱꜱᴀɢᴇ ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ"
            sql.set_blacklist_strength(chat_id, 1, "0")
        elif args[0].lower() == "warn":
            settypeblacklist = "ᴡᴀʀɴᴇᴅ"
            sql.set_blacklist_strength(chat_id, 2, "0")
        elif args[0].lower() == "mute":
            settypeblacklist = "ᴍᴜᴛᴇᴅ"
            sql.set_blacklist_strength(chat_id, 3, "0")
        elif args[0].lower() == "kick":
            settypeblacklist = "ᴋɪᴄᴋᴇᴅ"
            sql.set_blacklist_strength(chat_id, 4, "0")
        elif args[0].lower() == "ban":
            settypeblacklist = "ʙᴀɴɴᴇᴅ"
            sql.set_blacklist_strength(chat_id, 5, "0")
        elif args[0].lower() == "tban":
            if len(args) == 1:
                teks = """» ɪᴛ ʟᴏᴏᴋꜱ ʟɪᴋᴇ ʏᴏᴜ ᴀʀᴇ ᴛʀʏɪɴɢ ᴛᴏ ꜱᴇᴛ ᴀ ᴛᴇᴍᴘᴏʀᴀʀʏ ᴠᴀʟᴜᴇ ᴛᴏ ʙʟᴀᴄᴋʟɪꜱᴛ, ʙᴜᴛ ʜᴀꜱ ɴᴏᴛ ᴅᴇᴛᴇʀᴍɪɴᴇᴅ ᴛʜᴇ ᴛɪᴍᴇ; ᴜꜱᴇ `/blstickermode tban <timevalue>`.\n\n» ᴇxᴀᴍᴘʟᴇꜱ ᴏꜰ ᴛɪᴍᴇ ᴠᴀʟᴜᴇꜱ: 4m = 4 minute, 3h = 3 hours, 6d = 6 days, 5w = 5 weeks."""
                send_message(update.effective_message, teks, parse_mode="markdown")
                return
            settypeblacklist = "ᴛᴇᴍᴘᴏʀᴀʀʏ ʙᴀɴɴᴇᴅ ꜰᴏʀ {}".format(args[1])
            sql.set_blacklist_strength(chat_id, 6, str(args[1]))
        elif args[0].lower() == "tmute":
            if len(args) == 1:
                teks = """» ɪᴛ ʟᴏᴏᴋꜱ ʟɪᴋᴇ ʏᴏᴜ ᴀʀᴇ ᴛʀʏɪɴɢ ᴛᴏ ꜱᴇᴛ ᴀ ᴛᴇᴍᴘᴏʀᴀʀʏ ᴠᴀʟᴜᴇ ᴛᴏ ʙʟᴀᴄᴋʟɪꜱᴛ, ʙᴜᴛ ʜᴀꜱ ɴᴏᴛ ᴅᴇᴛᴇʀᴍɪɴᴇᴅ ᴛʜᴇ ᴛɪᴍᴇ; ᴜꜱᴇ `/blstickermode tmute <timevalue>`.\n\n» ᴇxᴀᴍᴘʟᴇꜱ ᴏꜰ ᴛɪᴍᴇ ᴠᴀʟᴜᴇꜱ: 4m = 4 minute, 3h = 3 hours, 6d = 6 days, 5w = 5 weeks."""
                send_message(update.effective_message, teks, parse_mode="markdown")
                return
            settypeblacklist = "ᴛᴇᴍᴘᴏʀᴀʀʏ ᴍᴜᴛᴇᴅ ꜰᴏʀ {}".format(args[1])
            sql.set_blacklist_strength(chat_id, 7, str(args[1]))
        else:
            send_message(
                update.effective_message,
                "I only understand off/del/warn/ban/kick/mute/tban/tmute!",
            )
            return
        if conn:
            text = "» ʙʟᴀᴄᴋʟɪꜱᴛ ꜱᴛɪᴄᴋᴇʀ ᴍᴏᴅᴇ ᴄʜᴀɴɢᴇᴅ, ᴜꜱᴇʀꜱ ᴡɪʟʟ ʙᴇ `{}` ᴀᴛ *{}*!".format(settypeblacklist, chat_name)
        else:
            text = "» ʙʟᴀᴄᴋʟɪꜱᴛ ꜱᴛɪᴄᴋᴇʀ ᴍᴏᴅᴇ ᴄʜᴀɴɢᴇᴅ, ᴜꜱᴇʀꜱ ᴡɪʟʟ ʙᴇ `{}`!".format(settypeblacklist)
        send_message(update.effective_message, text, parse_mode="markdown")
        return
    else:
        getmode, getvalue = sql.get_blacklist_setting(chat.id)
        if getmode == 0:
            settypeblacklist = "ɴᴏᴛ ᴀᴄᴛɪᴠᴇ"
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
            settypeblacklist = "ᴛᴇᴍᴘᴏʀᴀʀʏ ʙᴀɴɴᴇᴅ ꜰᴏʀ {}".format(getvalue)
        elif getmode == 7:
            settypeblacklist = "ᴛᴇᴍᴘᴏʀᴀʀʏ ᴍᴜᴛᴇᴅ ꜰᴏʀ {}".format(getvalue)
        if conn:
            text = "» ʙʟᴀᴄᴋʟɪꜱᴛ ꜱᴛɪᴄᴋᴇʀ ᴍᴏᴅᴇ ɪꜱ ᴄᴜʀʀᴇɴᴛʟʏ ꜱᴇᴛ ᴛᴏ *{}* ɪɴ *{}*.".format(
                settypeblacklist, chat_name
            )
        else:
            text = "» ʙʟᴀᴄᴋʟɪꜱᴛ ꜱᴛɪᴄᴋᴇʀ ᴍᴏᴅᴇ ɪꜱ ᴄᴜʀʀᴇɴᴛʟʏ ꜱᴇᴛ ᴛᴏ *{}*.".format(
                settypeblacklist
            )
        send_message(update.effective_message, text, parse_mode=ParseMode.MARKDOWN)
    return ""


@run_async
@user_not_admin
def del_blackliststicker(update: Update, context: CallbackContext):
    bot = context.bot
    chat = update.effective_chat
    message = update.effective_message
    user = update.effective_user
    to_match = message.sticker
    if not to_match or not to_match.set_name:
        return
    bot = context.bot
    getmode, value = sql.get_blacklist_setting(chat.id)

    chat_filters = sql.get_chat_stickers(chat.id)
    for trigger in chat_filters:
        if to_match.set_name.lower() == trigger.lower():
            try:
                if getmode == 0:
                    return
                elif getmode == 1:
                    message.delete()
                elif getmode == 2:
                    message.delete()
                    warn(
                        update.effective_user,
                        chat,
                        "» ᴜꜱɪɴɢ ꜱᴛɪᴄᴋᴇʀ '{}' ᴡʜɪᴄʜ ɪɴ ʙʟᴀᴄᴋʟɪꜱᴛ ꜱᴛɪᴄᴋᴇʀꜱ".format(
                            trigger
                        ),
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
                        "» {} ᴍᴜᴛᴇᴅ ʙᴇᴄᴀᴜꜱᴇ ᴜꜱɪɴɢ '{}' ᴡʜɪᴄʜ ɪɴ ʙʟᴀᴄᴋʟɪꜱᴛ ꜱᴛɪᴄᴋᴇʀꜱ".format(
                            mention_markdown(user.id, user.first_name), trigger
                        ),
                        parse_mode="markdown",
                    )
                    return
                elif getmode == 4:
                    message.delete()
                    res = chat.unban_member(update.effective_user.id)
                    if res:
                        bot.sendMessage(
                            chat.id,
                            "» {} ᴋɪᴄᴋᴇᴅ ʙᴇᴄᴀᴜꜱᴇ ᴜꜱɪɴɢ '{}' ᴡʜɪᴄʜ ɪɴ ʙʟᴀᴄᴋʟɪꜱᴛ ꜱᴛɪᴄᴋᴇʀꜱ".format(
                                mention_markdown(user.id, user.first_name), trigger
                            ),
                            parse_mode="markdown",
                        )
                    return
                elif getmode == 5:
                    message.delete()
                    chat.kick_member(user.id)
                    bot.sendMessage(
                        chat.id,
                        "» {} ʙᴀɴɴᴇᴅ ʙᴇᴄᴀᴜꜱᴇ ᴜꜱɪɴɢ '{}' ᴡʜɪᴄʜ ɪɴ ʙʟᴀᴄᴋʟɪꜱᴛ ꜱᴛɪᴄᴋᴇʀꜱ".format(
                            mention_markdown(user.id, user.first_name), trigger
                        ),
                        parse_mode="markdown",
                    )
                    return
                elif getmode == 6:
                    message.delete()
                    bantime = extract_time(message, value)
                    chat.kick_member(user.id, until_date=bantime)
                    bot.sendMessage(
                        chat.id,
                        "» {} ʙᴀɴɴᴇᴅ ꜰᴏʀ {} ʙᴇᴄᴀᴜꜱᴇ ᴜꜱɪɴɢ '{}' ᴡʜɪᴄʜ ɪɴ ʙʟᴀᴄᴋʟɪꜱᴛ ꜱᴛɪᴄᴋᴇʀꜱ".format(
                            mention_markdown(user.id, user.first_name), value, trigger
                        ),
                        parse_mode="markdown",
                    )
                    return
                elif getmode == 7:
                    message.delete()
                    mutetime = extract_time(message, value)
                    bot.restrict_chat_member(
                        chat.id,
                        user.id,
                        permissions=ChatPermissions(can_send_messages=False),
                        until_date=mutetime,
                    )
                    bot.sendMessage(
                        chat.id,
                        "» {} ᴍᴜᴛᴇᴅ ꜰᴏʀ {} ʙᴇᴄᴀᴜꜱᴇ ᴜꜱɪɴɢ '{}' ᴡʜɪᴄʜ ɪɴ ʙʟᴀᴄᴋʟɪꜱᴛ ꜱᴛɪᴄᴋᴇʀꜱ".format(
                            mention_markdown(user.id, user.first_name), value, trigger
                        ),
                        parse_mode="markdown",
                    )
                    return
            except BadRequest as excp:
                if excp.message != "Message to delete not found":
                    LOGGER.exception("Error while deleting blacklist message.")
                break


def __import_data__(chat_id, data):
    # set chat blacklist
    blacklist = data.get("sticker_blacklist", {})
    for trigger in blacklist:
        sql.add_to_stickers(chat_id, trigger)


def __migrate__(old_chat_id, new_chat_id):
    sql.migrate_chat(old_chat_id, new_chat_id)


def __chat_settings__(chat_id, user_id):
    blacklisted = sql.num_stickers_chat_filters(chat_id)
    return "» ᴛʜᴇʀᴇ ᴀʀᴇ `{} `ʙʟᴀᴄᴋʟɪꜱᴛᴇᴅ ꜱᴛɪᴄᴋᴇʀꜱ.".format(blacklisted)


def __stats__():
    return "• {} ʙʟᴀᴄᴋʟɪꜱᴛ ꜱᴛɪᴄᴋᴇʀꜱ, ᴀᴄʀᴏꜱꜱ {} ᴄʜᴀᴛꜱ.".format(
        sql.num_stickers_filters(), sql.num_stickers_filter_chats()
    )


__help__ = """
‣ ʙʟᴀᴄᴋʟɪꜱᴛ ꜱᴛɪᴄᴋᴇʀ ɪꜱ ᴜꜱᴇᴅ ᴛᴏ ꜱᴛᴏᴘ ᴄᴇʀᴛᴀɪɴ ꜱᴛɪᴄᴋᴇʀꜱ. ᴡʜᴇɴᴇᴠᴇʀ ᴀ ꜱᴛɪᴄᴋᴇʀ ɪꜱ ꜱᴇɴᴛ, ᴛʜᴇ ᴍᴇꜱꜱᴀɢᴇ ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ ɪᴍᴍᴇᴅɪᴀᴛᴇʟʏ.

  ➲ /blsticker: See current blacklisted sticker

𝗔𝗱𝗺𝗶𝗻𝘀 𝗼𝗻𝗹𝘆:
  ➲ /addblsticker <sticker link>: ᴀᴅᴅ ᴛʜᴇ ꜱᴛɪᴄᴋᴇʀ ᴛʀɪɢɢᴇʀ ᴛᴏ ᴛʜᴇ ʙʟᴀᴄᴋ ʟɪꜱᴛ. ᴄᴀɴ ʙᴇ ᴀᴅᴅᴇᴅ ᴠɪᴀ ʀᴇᴘʟʏ ꜱᴛɪᴄᴋᴇʀ
  ➲ /unblsticker <sticker link>: ʀᴇᴍᴏᴠᴇ ᴛʀɪɢɢᴇʀꜱ ꜰʀᴏᴍ ʙʟᴀᴄᴋʟɪꜱᴛ. ᴛʜᴇ ꜱᴀᴍᴇ ɴᴇᴡʟɪɴᴇ ʟᴏɢɪᴄ ᴀᴘᴘʟɪᴇꜱ ʜᴇʀᴇ, ꜱᴏ ʏᴏᴜ ᴄᴀɴ ᴅᴇʟᴇᴛᴇ ᴍᴜʟᴛɪᴘʟᴇ ᴛʀɪɢɢᴇʀꜱ ᴀᴛ ᴏɴᴄᴇ
  ➲ /rmblsticker <sticker link>: ꜱᴀᴍᴇ ᴀꜱ ᴀʙᴏᴠᴇ
  ➲ /blstickermode <ban/tban/mute/tmute>: ꜱᴇᴛꜱ ᴜᴘ ᴀ ᴅᴇꜰᴀᴜʟᴛ ᴀᴄᴛɪᴏɴ ᴏɴ ᴡʜᴀᴛ ᴛᴏ ᴅᴏ ɪꜰ ᴜꜱᴇʀꜱ ᴜꜱᴇ ʙʟᴀᴄᴋʟɪꜱᴛᴇᴅ ꜱᴛɪᴄᴋᴇʀꜱ

⚠ 𝗡𝗼𝘁𝗲:
   » ʙʟᴀᴄᴋʟɪꜱᴛ ꜱᴛɪᴄᴋᴇʀꜱ ᴅᴏ ɴᴏᴛ ᴀꜰꜰᴇᴄᴛ ᴛʜᴇ ɢʀᴏᴜᴘ ᴀᴅᴍɪɴ
   » <sticker link> ᴄᴀɴ ʙᴇ `https://t.me/addstickers/<sticker>` ᴏʀ ᴊᴜꜱᴛ `<sticker>` ᴏʀ ʀᴇᴘʟʏ ᴛᴏ ᴛʜᴇ ꜱᴛɪᴄᴋᴇʀ ᴍᴇꜱꜱᴀɢᴇ
"""

__mod_name__ = "Bʟ-Sᴛɪᴄᴋ"

BLACKLIST_STICKER_HANDLER = DisableAbleCommandHandler(
    "blsticker", blackliststicker, admin_ok=True
)
ADDBLACKLIST_STICKER_HANDLER = DisableAbleCommandHandler(
    "addblsticker", add_blackliststicker
)
UNBLACKLIST_STICKER_HANDLER = CommandHandler(
    ["unblsticker", "rmblsticker"], unblackliststicker
)
BLACKLISTMODE_HANDLER = CommandHandler("blstickermode", blacklist_mode)
BLACKLIST_STICKER_DEL_HANDLER = MessageHandler(
    Filters.sticker & Filters.group, del_blackliststicker
)

dispatcher.add_handler(BLACKLIST_STICKER_HANDLER)
dispatcher.add_handler(ADDBLACKLIST_STICKER_HANDLER)
dispatcher.add_handler(UNBLACKLIST_STICKER_HANDLER)
dispatcher.add_handler(BLACKLISTMODE_HANDLER)
dispatcher.add_handler(BLACKLIST_STICKER_DEL_HANDLER)
