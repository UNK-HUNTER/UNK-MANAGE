from telethon import custom, events

from AltronRobot import telethn as bot
from AltronRobot.events import register


@register(pattern="/myinfo")
async def pythonx(event):
    firstname = event.sender.first_name
    button = [[custom.Button.inline("• ɪɴꜰᴏʀᴍᴀᴛɪᴏɴ •", data="information")]]
    await bot.send_file(
        event.chat_id,
        file="https://telegra.ph/file/701028ce085ecfa961a36.jpg",
        caption=f"» ʜᴇʏ {firstname},\n ᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴛᴏ ɢᴇᴛ ɪɴꜰᴏ ᴀʙᴏᴜᴛ ʏᴏᴜ.",
        buttons=button,
    )


@bot.on(events.callbackquery.CallbackQuery(data="information"))
async def callback_query_handler(event):
    try:
        alt = event.sender_id
        PRO = await bot.get_entity(alt)
        LILIE = "𝗣𝗼𝘄𝗲𝗿𝗲𝗱 𝗯𝘆 𝗔𝗹𝘁𝗿𝗼𝗻:\n\n"
        LILIE += f" • ꜰɪʀꜱᴛ ɴᴀᴍᴇ : {PRO.first_name}\n"
        LILIE += f" • ʟᴀꜱᴛ ɴᴀᴍᴇ : {PRO.last_name}\n"
        LILIE += f" • ʏᴏᴜ ʙᴏᴛ : {PRO.bot}\n"
        LILIE += f" • ʀᴇꜱᴛʀɪᴄᴛᴇᴅ : {PRO.restricted}\n"
        LILIE += f" • ᴜꜱᴇʀ ɪᴅ : {alt}\n"
        LILIE += f" • ᴜꜱᴇʀɴᴀᴍᴇ : {PRO.username}\n"
        await event.answer(LILIE, alert=True)
    except Exception as e:
        await event.reply(f"{e}")

__command_list__ = ["myinfo"]
