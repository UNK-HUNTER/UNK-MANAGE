import json
import os
import time
from io import BytesIO

from telegram import ParseMode
from telegram.error import BadRequest
from telegram.ext import CommandHandler, run_async

import AltronRobot.modules.sql.blacklist_sql as blacklistsql
import AltronRobot.modules.sql.locks_sql as locksql
import AltronRobot.modules.sql.notes_sql as sql
import AltronRobot.modules.sql.rules_sql as rulessql
from AltronRobot import JOIN_LOGGER, LOGGER, OWNER_ID, SUPPORT_CHAT, dispatcher
from AltronRobot.__main__ import DATA_IMPORT
from AltronRobot.modules.connection import connected
from AltronRobot.modules.helper_funcs.alternate import typing_action
from AltronRobot.modules.helper_funcs.chat_status import user_admin
from AltronRobot.modules.sql import disable_sql as disabledsql


@run_async
@user_admin
@typing_action
def import_data(update, context):
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    conn = connected(context.bot, update, chat, user.id, need_admin=True)
    if conn:
        chat = dispatcher.bot.getChat(conn)
        chat_name = dispatcher.bot.getChat(conn).title
    else:
        if update.effective_message.chat.type == "private":
            update.effective_message.reply_text("» ᴛʜɪꜱ ɪꜱ ᴀ ɢʀᴏᴜᴘ ᴏɴʟʏ ᴄᴏᴍᴍᴀɴᴅ!")
            return ""

        chat = update.effective_chat
        chat_name = update.effective_message.chat.title

    if msg.reply_to_message and msg.reply_to_message.document:
        try:
            file_info = context.bot.get_file(msg.reply_to_message.document.file_id)
        except BadRequest:
            msg.reply_text(
                "» ᴛʀʏ ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ᴀɴᴅ ᴜᴘʟᴏᴀᴅɪɴɢ ᴛʜᴇ ꜰɪʟᴇ ʏᴏᴜʀꜱᴇʟꜰ ᴀɢᴀɪɴ, ᴛʜɪꜱ ᴏɴᴇ ꜱᴇᴇᴍ ʙʀᴏᴋᴇɴ ᴛᴏ ᴍᴇ!"
            )
            return

        with BytesIO() as file:
            file_info.download(out=file)
            file.seek(0)
            data = json.load(file)

        # only import one group
        if len(data) > 1 and str(chat.id) not in data:
            msg.reply_text(
                "» ᴛʜᴇʀᴇ ᴀʀᴇ ᴍᴏʀᴇ ᴛʜᴀɴ ᴏɴᴇ ɢʀᴏᴜᴘ ɪɴ ᴛʜɪꜱ ꜰɪʟᴇ ᴀɴᴅ ᴛʜᴇ ᴄʜᴀᴛ.ɪᴅ ɪꜱ ɴᴏᴛ ꜱᴀᴍᴇ! ʜᴏᴡ ᴀᴍ ɪ ꜱᴜᴘᴘᴏꜱᴇᴅ ᴛᴏ ɪᴍᴘᴏʀᴛ ɪᴛ?"
            )
            return

        # Check if backup is this chat
        try:
            if data.get(str(chat.id)) is None:
                if conn:
                    text = f"» ʙᴀᴄᴋᴜᴘ ᴄᴏᴍᴇꜱ ꜰʀᴏᴍ ᴀɴᴏᴛʜᴇʀ ᴄʜᴀᴛ, ɪ ᴄᴀɴ'ᴛ ʀᴇᴛᴜʀɴ ᴀɴᴏᴛʜᴇʀ ᴄʜᴀᴛ ᴛᴏ ᴄʜᴀᴛ *{chat_name}*"
                else:
                    text = "» ʙᴀᴄᴋᴜᴘ ᴄᴏᴍᴇꜱ ꜰʀᴏᴍ ᴀɴᴏᴛʜᴇʀ ᴄʜᴀᴛ, ɪ ᴄᴀɴ'ᴛ ʀᴇᴛᴜʀɴ ᴀɴᴏᴛʜᴇʀ ᴄʜᴀᴛ ᴛᴏ ᴛʜɪꜱ ᴄʜᴀᴛ"
                return msg.reply_text(text, parse_mode="markdown")
        except Exception:
            return msg.reply_text("» ᴛʜᴇʀᴇ ᴡᴀꜱ ᴀ ᴘʀᴏʙʟᴇᴍ ᴡʜɪʟᴇ ɪᴍᴘᴏʀᴛɪɴɢ ᴛʜᴇ ᴅᴀᴛᴀ!")
        # Check if backup is from self
        try:
            if str(context.bot.id) != str(data[str(chat.id)]["bot"]):
                return msg.reply_text(
                    "» ʙᴀᴄᴋᴜᴘ ꜰʀᴏᴍ ᴀɴᴏᴛʜᴇʀ ʙᴏᴛ ᴛʜᴀᴛ ɪꜱ ɴᴏᴛ ꜱᴜɢɢᴇꜱᴛᴇᴅ ᴍɪɢʜᴛ ᴄᴀᴜꜱᴇ ᴛʜᴇ ᴘʀᴏʙʟᴇᴍ, ᴅᴏᴄᴜᴍᴇɴᴛꜱ, ᴘʜᴏᴛᴏꜱ, ᴠɪᴅᴇᴏꜱ, ᴀᴜᴅɪᴏꜱ, ʀᴇᴄᴏʀᴅꜱ ᴍɪɢʜᴛ ɴᴏᴛ ᴡᴏʀᴋ ᴀꜱ ɪᴛ ꜱʜᴏᴜʟᴅ ʙᴇ."
                )
        except Exception:
            pass
        # Select data source
        if str(chat.id) in data:
            data = data[str(chat.id)]["hashes"]
        else:
            data = data[list(data.keys())[0]]["hashes"]

        try:
            for mod in DATA_IMPORT:
                mod.__import_data__(str(chat.id), data)
        except Exception:
            msg.reply_text(
                f"» ᴀɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ ᴡʜɪʟᴇ ʀᴇᴄᴏᴠᴇʀɪɴɢ ʏᴏᴜʀ ᴅᴀᴛᴀ. ᴛʜᴇ ᴘʀᴏᴄᴇꜱꜱ ꜰᴀɪʟᴇᴅ. ɪꜰ ʏᴏᴜ ᴇxᴘᴇʀɪᴇɴᴄᴇ ᴀ ᴘʀᴏʙʟᴇᴍ ᴡɪᴛʜ ᴛʜɪꜱ, ᴘʟᴇᴀꜱᴇ ᴛᴀᴋᴇ ɪᴛ ᴛᴏ @{SUPPORT_CHAT}"
            )

            LOGGER.exception(
                "Imprt for the chat %s with the name %s failed.",
                str(chat.id),
                str(chat.title),
            )
            return

        # TODO: some of that link logic
        # NOTE: consider default permissions stuff?
        if conn:
            text = f"» ʙᴀᴄᴋᴜᴘ ꜰᴜʟʟʏ ʀᴇꜱᴛᴏʀᴇᴅ ᴏɴ *{chat_name}*."
        else:
            text = "» ʙᴀᴄᴋᴜᴘ ꜰᴜʟʟʏ ʀᴇꜱᴛᴏʀᴇᴅ"
        msg.reply_text(text, parse_mode="markdown")


@run_async
@user_admin
def export_data(update, context):
    chat_data = context.chat_data
    msg = update.effective_message
    user = update.effective_user
    chat_id = update.effective_chat.id
    chat = update.effective_chat
    current_chat_id = update.effective_chat.id
    conn = connected(context.bot, update, chat, user.id, need_admin=True)
    if conn:
        chat = dispatcher.bot.getChat(conn)
        chat_id = conn
    else:
        if update.effective_message.chat.type == "private":
            update.effective_message.reply_text("» ᴛʜɪꜱ ɪꜱ ᴀ ɢʀᴏᴜᴘ ᴏɴʟʏ ᴄᴏᴍᴍᴀɴᴅ!")
            return ""
        chat = update.effective_chat
        chat_id = update.effective_chat.id

    jam = time.time()
    new_jam = jam + 10800
    checkchat = get_chat(chat_id, chat_data)
    if checkchat.get("status"):
        if jam <= int(checkchat.get("value")):
            timeformatt = time.strftime(
                "%H:%M:%S %d/%m/%Y", time.localtime(checkchat.get("value"))
            )
            update.effective_message.reply_text(
                "» ʏᴏᴜ ᴄᴀɴ ᴏɴʟʏ ʙᴀᴄᴋᴜᴘ ᴏɴᴄᴇ ᴀ ᴅᴀʏ!\n» ʏᴏᴜ ᴄᴀɴ ʙᴀᴄᴋᴜᴘ ᴀɢᴀɪɴ ɪɴ ᴀʙᴏᴜᴛ `{}`".format(
                    timeformatt
                ),
                parse_mode=ParseMode.MARKDOWN,
            )
            return
        else:
            if user.id != OWNER_ID:
                put_chat(chat_id, new_jam, chat_data)
    else:
        if user.id != OWNER_ID:
            put_chat(chat_id, new_jam, chat_data)

    note_list = sql.get_all_chat_notes(chat_id)
    backup = {}
    buttonlist = []
    namacat = ""
    isicat = ""
    rules = ""
    count = 0
    countbtn = 0
    # Notes
    for note in note_list:
        count += 1
        namacat += "{}<###splitter###>".format(note.name)
        if note.msgtype == 1:
            tombol = sql.get_buttons(chat_id, note.name)
            for btn in tombol:
                countbtn += 1
                if btn.same_line:
                    buttonlist.append(
                        ("{}".format(btn.name), "{}".format(btn.url), True)
                    )
                else:
                    buttonlist.append(
                        ("{}".format(btn.name), "{}".format(btn.url), False)
                    )
            isicat += "###button###: {}<###button###>{}<###splitter###>".format(
                note.value, str(buttonlist)
            )
            buttonlist.clear()
        elif note.msgtype == 2:
            isicat += "###sticker###:{}<###splitter###>".format(note.file)
        elif note.msgtype == 3:
            isicat += "###file###:{}<###TYPESPLIT###>{}<###splitter###>".format(
                note.file, note.value
            )
        elif note.msgtype == 4:
            isicat += "###photo###:{}<###TYPESPLIT###>{}<###splitter###>".format(
                note.file, note.value
            )
        elif note.msgtype == 5:
            isicat += "###audio###:{}<###TYPESPLIT###>{}<###splitter###>".format(
                note.file, note.value
            )
        elif note.msgtype == 6:
            isicat += "###voice###:{}<###TYPESPLIT###>{}<###splitter###>".format(
                note.file, note.value
            )
        elif note.msgtype == 7:
            isicat += "###video###:{}<###TYPESPLIT###>{}<###splitter###>".format(
                note.file, note.value
            )
        elif note.msgtype == 8:
            isicat += "###video_note###:{}<###TYPESPLIT###>{}<###splitter###>".format(
                note.file, note.value
            )
        else:
            isicat += "{}<###splitter###>".format(note.value)
    notes = {
        "#{}".format(namacat.split("<###splitter###>")[x]): "{}".format(
            isicat.split("<###splitter###>")[x]
        )
        for x in range(count)
    }
    # Rules
    rules = rulessql.get_rules(chat_id)
    # Blacklist
    bl = list(blacklistsql.get_chat_blacklist(chat_id))
    # Disabled command
    disabledcmd = list(disabledsql.get_all_disabled(chat_id))
    curr_locks = locksql.get_locks(chat_id)
    curr_restr = locksql.get_restr(chat_id)

    if curr_locks:
        locked_lock = {
            "sticker": curr_locks.sticker,
            "audio": curr_locks.audio,
            "voice": curr_locks.voice,
            "document": curr_locks.document,
            "video": curr_locks.video,
            "contact": curr_locks.contact,
            "photo": curr_locks.photo,
            "gif": curr_locks.gif,
            "url": curr_locks.url,
            "bots": curr_locks.bots,
            "forward": curr_locks.forward,
            "game": curr_locks.game,
            "location": curr_locks.location,
            "rtl": curr_locks.rtl,
        }
    else:
        locked_lock = {}

    if curr_restr:
        locked_restr = {
            "messages": curr_restr.messages,
            "media": curr_restr.media,
            "other": curr_restr.other,
            "previews": curr_restr.preview,
            "all": all(
                [
                    curr_restr.messages,
                    curr_restr.media,
                    curr_restr.other,
                    curr_restr.preview,
                ]
            ),
        }
    else:
        locked_restr = {}

    locks = {"locks": locked_lock, "restrict": locked_restr}
    # Backing up
    backup[chat_id] = {
        "bot": context.bot.id,
        "hashes": {
            "info": {"rules": rules},
            "extra": notes,
            "blacklist": bl,
            "disabled": disabledcmd,
            "locks": locks,
        },
    }
    baccinfo = json.dumps(backup, indent=4)
    with open("AltronRobot{}.backup".format(chat_id), "w") as f:
        f.write(str(baccinfo))
    context.bot.sendChatAction(current_chat_id, "upload_document")
    tgl = time.strftime("%H:%M:%S - %d/%m/%Y", time.localtime(time.time()))
    try:
        context.bot.sendMessage(
            JOIN_LOGGER,
            "» *ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ɪᴍᴘᴏʀᴛᴇᴅ ʙᴀᴄᴋᴜᴘ:*\n - ᴄʜᴀᴛ: `{}`\n - ᴄʜᴀᴛ ɪᴅ: `{}`\n - ᴏɴ: `{}`".format(
                chat.title, chat_id, tgl
            ),
            parse_mode=ParseMode.MARKDOWN,
        )
    except BadRequest:
        pass
    context.bot.sendDocument(
        current_chat_id,
        document=open("AltronRobot{}.backup".format(chat_id), "rb"),
        caption="» *ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ᴇxᴘᴏʀᴛᴇᴅ ʙᴀᴄᴋᴜᴘ:*\n - ᴄʜᴀᴛ: `{}`\n - ᴄʜᴀᴛ ɪᴅ: `{}`\n - ᴏɴ: `{}`\n\n⚠ 𝗡𝗼𝘁𝗲: ᴛʜɪꜱ `AltronRobot-Backup` ᴡᴀꜱ ꜱᴘᴇᴄɪᴀʟʟʏ ᴍᴀᴅᴇ ꜰᴏʀ ɴᴏᴛᴇꜱ 📚.".format(
            chat.title, chat_id, tgl
        ),
        timeout=360,
        reply_to_message_id=msg.message_id,
        parse_mode=ParseMode.MARKDOWN,
    )
    os.remove("AltronRobot{}.backup".format(chat_id))  # Cleaning file


# Temporary data
def put_chat(chat_id, value, chat_data):
    status = value is not False
    chat_data[chat_id] = {"backups": {"status": status, "value": value}}


def get_chat(chat_id, chat_data):
    try:
        return chat_data[chat_id]["backups"]
    except KeyError:
        return {"status": False, "value": False}


__mod_name__ = "Bᴀᴄᴋᴜᴘ"

__help__ = """
𝗢𝗻𝗹𝘆 𝗳𝗼𝗿 𝗚𝗿𝗼𝘂𝗽 𝗢𝘄𝗻𝗲𝗿:

  ➲ /import: ʀᴇᴘʟʏ ᴛᴏ ᴛʜᴇ ʙᴀᴄᴋᴜᴘ ꜰɪʟᴇ ꜰᴏʀ ᴛʜᴇ ʙᴜᴛʟᴇʀ/ᴇᴍɪʟɪᴀ ɢʀᴏᴜᴘ ᴛᴏ ɪᴍᴘᴏʀᴛ ᴀꜱ ᴍᴜᴄʜ ᴀꜱ ᴘᴏꜱꜱɪʙʟᴇ, ᴍᴀᴋɪɴɢ ᴛʀᴀɴꜱꜰᴇʀꜱ ᴠᴇʀʏ ᴇᴀꜱʏ!

  ➲ /export: ᴇxᴘᴏʀᴛ ɢʀᴏᴜᴘ ᴅᴀᴛᴀ, ᴡʜɪᴄʜ ᴡɪʟʟ ʙᴇ ᴇxᴘᴏʀᴛᴇᴅ ᴀʀᴇ: ʀᴜʟᴇꜱ, ɴᴏᴛᴇꜱ (ᴅᴏᴄᴜᴍᴇɴᴛꜱ, ɪᴍᴀɢᴇꜱ, ᴍᴜꜱɪᴄ, ᴠɪᴅᴇᴏ, ᴀᴜᴅɪᴏ, ᴠᴏɪᴄᴇ, ᴛᴇxᴛ, ᴛᴇxᴛ ʙᴜᴛᴛᴏɴꜱ)

 ⚠ 𝗡𝗼𝘁𝗲: ꜰɪʟᴇꜱ/ᴘʜᴏᴛᴏꜱ ᴄᴀɴɴᴏᴛ ʙᴇ ɪᴍᴘᴏʀᴛᴇᴅ ᴅᴜᴇ ᴛᴏ ᴛᴇʟᴇɢʀᴀᴍ ʀᴇꜱᴛʀɪᴄᴛɪᴏɴꜱ.
"""

IMPORT_HANDLER = CommandHandler("import", import_data)
EXPORT_HANDLER = CommandHandler("export", export_data, pass_chat_data=True)

dispatcher.add_handler(IMPORT_HANDLER)
dispatcher.add_handler(EXPORT_HANDLER)
