from pyrogram import filters

from AltronRobot import pbot
from AltronRobot.utils.errors import capture_err
from AltronRobot.utils.functions import make_carbon


@pbot.on_message(filters.command("carbon"))
@capture_err
async def carbon_func(_, message):
    Msg = message.text.split(" ")
    Text = ""
    if message.reply_to_message and len(Msg) == 1:
        Text = message.reply_to_message.text
    elif len(Msg) == 2:
        Text = Msg[1]
    else:
        return await message.reply_text("⚡ 𝗨𝘀𝗮𝗴𝗲: /carbon <ᴛᴇxᴛ> or <ʀᴇᴘʟʏ ᴛᴏ ᴛᴇxᴛ>")

    m = await message.reply_text("⚡ `ɢᴇɴᴇʀᴀᴛɪɴɢ ᴄᴀʀʙᴏɴ...`")
    carbon = await make_carbon(Text)
    await m.edit("`ᴜᴩʟᴏᴀᴅɪɴɢ ɢᴇɴᴇʀᴀᴛᴇᴅ ᴄᴀʀʙᴏɴ...`")
    await pbot.send_photo(message.chat.id, carbon)
    await m.delete()
    carbon.close()


__mod_name__ = "Cᴀʀʙᴏɴ"
__help__ = """
‣ ᴍᴀᴋᴇs ᴀ ᴄᴀʀʙᴏɴ ᴏғ ᴛʜᴇ ɢɪᴠᴇɴ ᴛᴇxᴛ ᴀɴᴅ sᴇɴᴅ ɪᴛ ᴛᴏ ʏᴏᴜ.
  ➲ /carbon <ᴛᴇxᴛ> or <ʀᴇᴘʟʏ ᴛᴏ ᴛᴇxᴛ>: ᴍᴀᴋᴇs ᴄᴀʀʙᴏɴ ᴏғ ᴀ ᴛᴇxᴛ
"""
