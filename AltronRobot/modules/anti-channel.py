from pyrogram import filters
from AltronRobot import pbot
from pyrogram.types import Message
from AltronRobot.modules.webshot import eor
from AltronRobot.utils.errors import capture_err

active_channel = []

async def channel_toggle(db, message: Message):
    status = message.text.split(None, 1)[1].lower()
    chat_id = message.chat.id

    if status == "on":
        if chat_id not in db:
            db.append(chat_id)
            return await eor(message, text="» ᴀɴᴛɪᴄʜᴀɴɴᴇʟ ᴇɴᴀʙʟᴇᴅ ✅")
        await eor(message, text="» ᴀɴᴛɪᴄʜᴀɴɴᴇʟ ɪꜱ ᴀʟʀᴇᴀᴅʏ ᴇɴᴀʙʟᴇᴅ.")
    elif status == "off":
        if chat_id in db:
            db.remove(chat_id)
            return await eor(message, text="» ᴀɴᴛɪᴄʜᴀɴɴᴇʟ ᴅɪꜱᴀʙʟᴇᴅ ❌")
        await eor(message, text=f"» ᴀɴᴛɪᴄʜᴀɴɴᴇʟ ɪꜱ ᴀʟʀᴇᴀᴅʏ ᴅɪꜱᴀʙʟᴇᴅ.")
    else:
        await eor(message, text="» ᴜꜱᴇ /antichannel ᴡɪᴛʜ `on` ᴏʀ `off`")


# Enabled | Disable antichannel
@pbot.on_message(filters.command("antichannel"))
@capture_err
async def antichannel_status(_, message: Message):
    if len(message.command) != 2:
        return await eor(message, text="» ᴜꜱᴇ /antichannel ᴡɪᴛʜ `on` ᴏʀ `off`")
    await channel_toggle(active_channel, message)


@pbot.on_message(
    (
        filters.document
        | filters.photo
        | filters.sticker
        | filters.animation
        | filters.video
        | filters.text
    )
    & ~filters.private,
    group=41,
)
async def anitchnl(_, message):
  chat_id = message.chat.id
  if message.sender_chat:
    sender = message.sender_chat.id 
    if message.chat.id not in active_channel:
        return
    if chat_id == sender:
        return
    else:
        await message.delete()   

__mod_name__ = "Aɴᴛɪ-Cʜᴀɴɴᴇʟ"
__help__ = """
𝗔𝗻𝘁𝗶-𝗖𝗵𝗮𝗻𝗻𝗲𝗹 𝗠𝗼𝗱𝘂𝗹𝗲:
  ➲ /antichannel `on` : ᴛᴜʀɴ ᴏɴ ᴀɴᴛɪᴄʜᴀɴɴᴇʟ ꜰᴜɴᴄᴛɪᴏɴ
  ➲ /antichannel `off` : ᴛᴜʀɴ ᴏꜰꜰ ᴀɴᴛɪᴄʜᴀɴɴᴇʟ ꜰᴜɴᴄᴛɪᴏɴ
 """
