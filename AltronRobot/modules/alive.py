import telethon
import pyrogram
import telegram

from telethon import Button
from AltronRobot import telethn as telethn
from AltronRobot.events import register


@register(pattern=("/alive"))
async def alive(event):
    TEXT = f"**ʜᴇʏ​ [{event.sender.first_name}](tg://user?id={event.sender.id}),\n\nɪ ᴀᴍ [ᴀʟᴛʀᴏɴ ✘ ʀᴏʙᴏᴛ](https://t.me/AltronXRobot)​**\n━━━━━━━━━━━━━━━━━━━\n\n"
    TEXT += f"» **ᴍʏ ᴅᴇᴠᴇʟᴏᴘᴇʀ​ : [✘](https://t.me/ItzExStar)** \n\n"
    TEXT += f"» **ʟɪʙʀᴀʀʏ ᴠᴇʀsɪᴏɴ :** `{telegram.__version__}` \n"
    TEXT += f"» **ᴛᴇʟᴇᴛʜᴏɴ ᴠᴇʀsɪᴏɴ :** `{telethon.__version__}` \n"
    TEXT += f"» **ᴘʏʀᴏɢʀᴀᴍ ᴠᴇʀsɪᴏɴ :** `{pyrogram.__version__}` \n━━━━━━━━━━━━━━━━━\n\n"
    BUTTON = [
        [
            Button.url("ʜᴇʟᴘ​", "https://t.me/AltronXRobot?start=help"),
            Button.url("sᴜᴘᴘᴏʀᴛ​", "https://t.me/TheAltron"),
        ]
    ]
    await telethn.send_file(event.chat_id, "https://te.legra.ph/file/1f417d13c7e201d86e91e.jpg", caption=TEXT, buttons=BUTTON)

__mod_name__ = "Aʟɪᴠᴇ"
