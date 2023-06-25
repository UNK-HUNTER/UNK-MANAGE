# © @ItzExStar

import asyncio
from io import BytesIO

from pyrogram import filters, Client
from pyrogram.types import Message
from pyrogram.errors import FloodWait

from telegram import Update
from telegram.error import BadRequest, Unauthorized
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    Filters,
    MessageHandler,
    run_async,
)

import AltronRobot.modules.sql.users_sql as sql
from AltronRobot import LOGGER, dispatcher, pbot, OWNER_ID, DEV_USERS
from AltronRobot.modules.helper_funcs.chat_status import dev_plus, sudo_plus

USERS_GROUP = 4
CHAT_GROUP = 5
MORE_DEV = DEV_USERS + [OWNER_ID]


def get_user_id(username):
    # ensure valid userid
    if len(username) <= 5:
        return None

    if username.startswith("@"):
        username = username[1:]

    users = sql.get_userid_by_name(username)

    if not users:
        return None
    elif len(users) == 1:
        return users[0].user_id
    else:
        for user_obj in users:
            try:
                userdat = dispatcher.bot.get_chat(user_obj.user_id)
                if userdat.username == username:
                    return userdat.id

            except BadRequest as excp:
                if excp.message == "Chat not found":
                    pass
                else:
                    LOGGER.exception("Error extracting user ID")

    return None


@pbot.on_message(filters.command("gcast") & filters.user(MORE_DEV))
async def braodcast_message(client: Client, message: Message):
    if message.reply_to_message:
        x = message.reply_to_message_id
        y = message.chat.id
    else:
        if len(message.command) < 2:
            return await message.reply_text(f"𝗨𝘀𝗮𝗴𝗲:\n » /gcast [MESSAGE] ᴏʀ [Reply to a Message]")
        query = message.text.split(None, 1)[1]
        for M in  ["-pin", "-chat", "-pinloud", "-user"]:
            if M in query:
                query = query.replace(M, "")
        if query == "":
            return await message.reply_text("» ᴘʟᴇᴀꜱᴇ ᴘʀᴏᴠɪᴅᴇ ꜱᴏᴍᴇ ᴛᴇxᴛ ᴛᴏ ʙʀᴏᴀᴅᴄᴀꜱᴛ.")

    # Bot broadcast inside chats
    if "-chat" in message.text:
        sent = 0
        pin = 0
        chats = []
        altchats = sql.get_all_chats()
        for chat in altchats:
            chats.append(int(chat.chat_id))
        for i in chats:
            try:
                m = (
                    await client.forward_messages(i, y, x)
                    if message.reply_to_message
                    else await client.send_message(i, text=query)
                )
                if "-pinloud" in message.text:
                    try:
                        await m.pin(disable_notification=False)
                        pin += 1
                    except Exception:
                        continue
                elif "-pin" in message.text:
                    try:
                        await m.pin(disable_notification=True)
                        pin += 1
                    except Exception:
                        continue
                sent += 1
            except FloodWait as e:
                flood_time = int(e.x)
                if flood_time > 200:
                    continue
                await asyncio.sleep(flood_time)
            except Exception:
                continue
        try:
            await message.reply_text("**» ʙʀᴏᴀᴅᴄᴀꜱᴛᴇᴅ ᴍᴇꜱꜱᴀɢᴇ ɪɴ {}  ᴄʜᴀᴛꜱ ᴡɪᴛʜ {} ᴘɪɴꜱ ꜰʀᴏᴍ ʙᴏᴛ.**".format(sent, pin))
        except:
            pass

    # Bot broadcasting to users
    if "-user" in message.text:
        alt = 0
        served_users = []
        altusers = sql.get_all_users()
        for user in altusers:
            served_users.append(int(user.user_id))
        for i in served_users:
            try:
                m = (
                    await client.forward_messages(i, y, x)
                    if message.reply_to_message
                    else await client.send_message(i, text=query)
                )
                alt += 1
            except FloodWait as e:
                flood_time = int(e.x)
                if flood_time > 200:
                    continue
                await asyncio.sleep(flood_time)
            except Exception:
                pass
        try:
            await message.reply_text("**» ʙʀᴏᴀᴅᴄᴀꜱᴛᴇᴅ ᴍᴇꜱꜱᴀɢᴇ ᴛᴏ {} ᴜꜱᴇʀꜱ.**".format(alt))
        except:
            pass


@run_async
def log_user(update: Update, context: CallbackContext):
    chat = update.effective_chat
    msg = update.effective_message

    sql.update_user(msg.from_user.id, msg.from_user.username, chat.id, chat.title)

    if msg.reply_to_message:
        sql.update_user(
            msg.reply_to_message.from_user.id,
            msg.reply_to_message.from_user.username,
            chat.id,
            chat.title,
        )

    if msg.forward_from:
        sql.update_user(msg.forward_from.id, msg.forward_from.username)


@run_async
@sudo_plus
def chats(update: Update, context: CallbackContext):
    all_chats = sql.get_all_chats() or []
    chatfile = "» ʟɪꜱᴛ ᴏꜰ ᴄʜᴀᴛꜱ:\n\n0. Chat name | Chat ID | Members count\n"
    P = 1
    for chat in all_chats:
        try:
            curr_chat = context.bot.getChat(chat.chat_id)
            curr_chat.get_member(context.bot.id)
            chat_members = curr_chat.get_members_count(context.bot.id)
            chatfile += "{}. {} | {} | {}\n".format(
                P, chat.chat_name, chat.chat_id, chat_members
            )
            P = P + 1
        except:
            pass

    with BytesIO(str.encode(chatfile)) as output:
        output.name = "AltChats.txt"
        update.effective_message.reply_document(
            document=output,
            filename="AltChats.txt",
            caption="» ʜᴇʀᴇ ʙᴇ ᴛʜᴇ ʟɪꜱᴛ ᴏꜰ ɢʀᴏᴜᴘꜱ ɪɴ ᴍʏ ᴅᴀᴛᴀʙᴀꜱᴇ.",
        )


@run_async
def chat_checker(update: Update, context: CallbackContext):
    bot = context.bot
    try:
        if update.effective_message.chat.get_member(bot.id).can_send_messages is False:
            bot.leaveChat(update.effective_message.chat.id)
    except Unauthorized:
        pass


def __user_info__(user_id):
    if user_id in [777000, 1087968824]:
        return """<b>➻ ᴄᴏᴍᴍᴏɴ ᴄʜᴀᴛs:</b> <code>???</code>"""
    if user_id == dispatcher.bot.id:
        return """<b>➻ ᴄᴏᴍᴍᴏɴ ᴄʜᴀᴛs:</b> <code>???</code>"""
    num_chats = sql.get_user_num_chats(user_id)
    return f"""<b>➻ ᴄᴏᴍᴍᴏɴ ᴄʜᴀᴛs:</b> <code>{num_chats}</code>"""


def __stats__():
    return f"• {sql.num_users()} ᴜꜱᴇʀꜱ, ᴀᴄʀᴏꜱꜱ {sql.num_chats()} ᴄʜᴀᴛꜱ"


def __migrate__(old_chat_id, new_chat_id):
    sql.migrate_chat(old_chat_id, new_chat_id)


__help__ = ""  # no help string

USER_HANDLER = MessageHandler(Filters.all & Filters.group, log_user)
CHAT_CHECKER_HANDLER = MessageHandler(Filters.all & Filters.group, chat_checker)
CHATLIST_HANDLER = CommandHandler("groups", chats)

dispatcher.add_handler(USER_HANDLER, USERS_GROUP)
dispatcher.add_handler(CHATLIST_HANDLER)
dispatcher.add_handler(CHAT_CHECKER_HANDLER, CHAT_GROUP)

__mod_name__ = "Users"
__handlers__ = [(USER_HANDLER, USERS_GROUP), CHATLIST_HANDLER]
