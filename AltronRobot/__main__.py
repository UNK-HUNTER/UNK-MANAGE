import importlib
import re
import time

from platform import python_version as y
from sys import argv
from typing import Optional

from pyrogram import __version__ as pyrover
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Update
from telegram import __version__ as telever
from telegram.error import (
    BadRequest,
    ChatMigrated,
    NetworkError,
    TelegramError,
    TimedOut,
    Unauthorized,
)
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    Filters,
    MessageHandler,
)
from telegram.ext.dispatcher import DispatcherHandlerStop, run_async
from telegram.utils.helpers import escape_markdown
from telethon import __version__ as tlhver

import AltronRobot.modules.sql.users_sql as sql
from AltronRobot import (
    BOT_NAME,
    BOT_USERNAME,
    CERT_PATH,
    DONATION_LINK,
    LOGGER,
    OWNER_ID,
    PORT,
    START_IMG,
    SUPPORT_CHAT,
    TOKEN,
    URL,
    WEBHOOK,
    StartTime,
    dispatcher,
    pbot,
    telethn,
    updater,
)

# needed to dynamically load modules
# NOTE: Module order is not guaranteed, specify that in the config file!
from AltronRobot.modules import ALL_MODULES
from AltronRobot.modules.helper_funcs.chat_status import is_user_admin
from AltronRobot.modules.helper_funcs.misc import paginate_modules


def get_readable_time(seconds: int) -> str:
    count = 0
    ping_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]

    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)

    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        ping_time += time_list.pop() + ", "

    time_list.reverse()
    ping_time += ":".join(time_list)

    return ping_time


PM_START_TEXT = """
*🤖 ʜᴇʏᴀ..!!!*

*⍟ ᴛʜɪs ɪs {} !*
✦───────────────────────✦
*✘ ᴛʜᴇ ᴍᴏsᴛ ᴩᴏᴡᴇʀғᴜʟ ᴛᴇʟᴇɢʀᴀᴍ ɢʀᴏᴜᴩ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ ʙᴏᴛ ᴡɪᴛʜ sᴏᴍᴇ ᴀᴡᴇsᴏᴍᴇ ᴀɴᴅ ᴜsᴇғᴜʟ ғᴇᴀᴛᴜʀᴇs.*
✦───────────────────────✦
*✘ ᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ ʜᴇʟᴩ ʙᴜᴛᴛᴏɴ ᴛᴏ ɢᴇᴛ ɪɴғᴏʀᴍᴀᴛɪᴏɴ ᴀʙᴏᴜᴛ ᴍʏ ᴍᴏᴅᴜʟᴇs ᴀɴᴅ ᴄᴏᴍᴍᴀɴᴅs ℹ️.*
"""

buttons = [
    [
        InlineKeyboardButton(
            text="➕ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ➕",
            url=f"https://t.me/{BOT_USERNAME}?startgroup=true",
        ),
    ],
    [
        InlineKeyboardButton(text="✘ ᴀʙᴏᴜᴛ ", callback_data="altron_"),
        InlineKeyboardButton(text="✘ sᴜᴩᴩᴏʀᴛ", url=f"https://t.me/{SUPPORT_CHAT}"),
    ],
    [
        InlineKeyboardButton(text="✘ ʜᴇʟᴩ ᴀɴᴅ ᴄᴏᴍᴍᴀɴᴅs", callback_data="help_back"),
    ],
]

HELP_STRINGS = f"""
*» {BOT_NAME} ᴇxᴄʟᴜsɪᴠᴇ ꜰᴇᴀᴛᴜʀᴇs*

➲ /start : ꜱᴛᴀʀᴛꜱ ᴍᴇ | ᴀᴄᴄᴏʀᴅɪɴɢ ᴛᴏ ᴍᴇ ʏᴏᴜ'ᴠᴇ ᴀʟʀᴇᴀᴅʏ ᴅᴏɴᴇ ɪᴛ​.
➲ /donate : sᴜᴘᴘᴏʀᴛ ᴍᴇ ʙʏ ᴅᴏɴᴀᴛɪɴɢ ꜰᴏʀ ᴍʏ ʜᴀʀᴅᴡᴏʀᴋ​.
➲ /help  : ᴀᴠᴀɪʟᴀʙʟᴇ ᴄᴏᴍᴍᴀɴᴅꜱ ꜱᴇᴄᴛɪᴏɴ.
  ‣ ɪɴ ᴘᴍ : ᴡɪʟʟ ꜱᴇɴᴅ ʏᴏᴜ ʜᴇʟᴘ​ ꜰᴏʀ ᴀʟʟ ꜱᴜᴘᴘᴏʀᴛᴇᴅ ᴍᴏᴅᴜʟᴇꜱ.
  ‣ ɪɴ ɢʀᴏᴜᴘ : ᴡɪʟʟ ʀᴇᴅɪʀᴇᴄᴛ ʏᴏᴜ ᴛᴏ ᴘᴍ, ᴡɪᴛʜ ᴀʟʟ ᴛʜᴀᴛ ʜᴇʟᴘ​ ᴍᴏᴅᴜʟᴇꜱ."""

DONATE_STRING = """🤖 ʜᴇʏᴀ,
  ʜᴀᴩᴩʏ ᴛᴏ ʜᴇᴀʀ ᴛʜᴀᴛ ʏᴏᴜ ᴡᴀɴɴᴀ ᴅᴏɴᴀᴛᴇ.

ʏᴏᴜ ᴄᴀɴ ᴅɪʀᴇᴄᴛʟʏ ᴄᴏɴᴛᴀᴄᴛ ᴍʏ [ᴅᴇᴠᴇʟᴏᴩᴇʀ](https://t.me/ItzExStar) ғᴏʀ ᴅᴏɴᴀᴛɪɴɢ ᴏʀ ʏᴏᴜ ᴄᴀɴ ᴠɪsɪᴛ ᴍʏ [sᴜᴩᴩᴏʀᴛ ᴄʜᴀᴛ](https://t.me/AltronChats) ᴀɴᴅ ᴀsᴋ ᴛʜᴇʀᴇ ᴀʙᴏᴜᴛ ᴅᴏɴᴀᴛɪᴏɴ."""

ALTRON_ABOUT = f"""
*🤖 ʜᴇʏᴀ..!!!*

*⍟ ᴛʜɪs ɪs ˹ᴀʟᴛʀᴏɴ ꭙ ʀᴏʙᴏᴛ​˼*
✦───────────────────────✦
  *✘ ᴀ ᴘᴏᴡᴇʀꜰᴜʟ ɢʀᴏᴜᴘ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ ʙᴏᴛ ʙᴜɪʟᴛ ᴛᴏ ʜᴇʟᴘ ʏᴏᴜ ᴍᴀɴᴀɢᴇ ʏᴏᴜʀ ɢʀᴏᴜᴘ ᴇᴀꜱɪʟʏ ᴀɴᴅ ᴛᴏ ᴘʀᴏᴛᴇᴄᴛ ʏᴏᴜʀ ɢʀᴏᴜᴘ ꜰʀᴏᴍ ꜱᴄᴀᴍᴍᴇʀꜱ ᴀɴᴅ ꜱᴘᴀᴍᴍᴇʀꜱ.*
  *✘ ᴡʀɪᴛᴛᴇɴ ɪɴ ᴩʏᴛʜᴏɴ ᴡɪᴛʜ sǫʟᴀʟᴄʜᴇᴍʏ ᴀɴᴅ ᴍᴏɴɢᴏᴅʙ ᴀs ᴅᴀᴛᴀʙᴀsᴇ.*

       ╔━━━━━━━━━━━━━╗
              ➻ ᴜsᴇʀs » {sql.num_users()}
                ➻ ᴄʜᴀᴛs » {sql.num_chats()}
       ╚━━━━━━━━━━━━━╝

➪  ɪ ᴄᴀɴ ʀᴇꜱᴛʀɪᴄᴛ ᴜꜱᴇʀꜱ.
➪  ɪ ʜᴀᴠᴇ ᴀɴ ᴀᴅᴠᴀɴᴄᴇᴅ ᴀɴᴛɪ-ꜰʟᴏᴏᴅ ꜱʏꜱᴛᴇᴍ.
➪  ɪ ᴄᴀɴ ɢʀᴇᴇᴛ ᴜꜱᴇʀꜱ ᴡɪᴛʜ ᴄᴜꜱᴛᴏᴍɪᴢᴀʙʟᴇ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇꜱꜱᴀɢᴇꜱ ᴀɴᴅ ᴇᴠᴇɴ ꜱᴇᴛ ᴀ ɢʀᴏᴜᴘ'ꜱ ʀᴜʟᴇꜱ.
➪  ɪ ᴄᴀɴ ᴡᴀʀɴ ᴜꜱᴇʀꜱ ᴜɴᴛɪʟ ᴛʜᴇʏ ʀᴇᴀᴄʜ ᴍᴀx ᴡᴀʀɴꜱ, ᴡɪᴛʜ ᴇᴀᴄʜ ᴘʀᴇᴅᴇꜰɪɴᴇᴅ ᴀᴄᴛɪᴏɴꜱ ꜱᴜᴄʜ ᴀꜱ ʙᴀɴ, ᴍᴜᴛᴇ, ᴋɪᴄᴋ, ᴇᴛᴄ.
➪  ɪ ʜᴀᴠᴇ ᴀ ɴᴏᴛᴇ ᴋᴇᴇᴘɪɴɢ ꜱʏꜱᴛᴇᴍ, ʙʟᴀᴄᴋʟɪꜱᴛꜱ, ᴀɴᴅ ᴇᴠᴇɴ ᴘʀᴇᴅᴇᴛᴇʀᴍɪɴᴇᴅ ʀᴇᴘʟɪᴇꜱ ᴏɴ ᴄᴇʀᴛᴀɪɴ ᴋᴇʏᴡᴏʀᴅꜱ.

✦───────────────────────✦
 *✘ ɪ ʜᴀᴠᴇ ʟᴏᴛꜱ ᴏꜰ ꜰᴇᴀᴛᴜʀᴇꜱ ᴡʜɪᴄʜ ʏᴏᴜ ʟɪᴋᴇꜱ ᴛʜᴀᴛ.*
"""

FedUsers = """
𝗙𝗲𝗱 𝗨𝘀𝗲𝗿 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀:
 ➲ /fstat: ꜱʜᴏᴡꜱ ɪꜰ ʏᴏᴜ/ᴏʀ ᴛʜᴇ ᴜꜱᴇʀ ʏᴏᴜ ᴀʀᴇ ʀᴇᴘʟʏɪɴɢ ᴛᴏ ᴏʀ ᴛʜᴇɪʀ ᴜꜱᴇʀɴᴀᴍᴇ ɪꜱ ꜰʙᴀɴɴᴇᴅ ꜱᴏᴍᴇᴡʜᴇʀᴇ ᴏʀ ɴᴏᴛ
 ➲ /fednotif <on/off>: ꜰᴇᴅᴇʀᴀᴛɪᴏɴ ꜱᴇᴛᴛɪɴɢꜱ ɴᴏᴛ ɪɴ ᴘᴍ ᴡʜᴇɴ ᴛʜᴇʀᴇ ᴀʀᴇ ᴜꜱᴇʀꜱ ᴡʜᴏ ᴀʀᴇ ꜰʙᴀɴᴇᴅ/ᴜɴꜰʙᴀɴɴᴇᴅ
 ➲ /frules: ꜱᴇᴇ ꜰᴇᴅᴇʀᴀᴛɪᴏɴ ʀᴇɢᴜʟᴀᴛɪᴏɴꜱ
"""

FedAdmins = """
𝗙𝗲𝗱 𝗔𝗱𝗺𝗶𝗻 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀:
 ➲ /fban <user> <reason>: ꜰᴇᴅ ʙᴀɴꜱ ᴀ ᴜꜱᴇʀ
 ➲ /unfban <user> <reason>: ʀᴇᴍᴏᴠᴇꜱ ᴀ ᴜꜱᴇʀ ꜰʀᴏᴍ ᴀ ꜰᴇᴅ ʙᴀɴ
 ➲ /fedinfo <fed_id>: ɪɴꜰᴏʀᴍᴀᴛɪᴏɴ ᴀʙᴏᴜᴛ ᴛʜᴇ ꜱᴘᴇᴄɪꜰɪᴇᴅ ꜰᴇᴅᴇʀᴀᴛɪᴏɴ
 ➲ /joinfed <fed_id>: ᴊᴏɪɴ ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ᴄʜᴀᴛ ᴛᴏ ᴛʜᴇ ꜰᴇᴅᴇʀᴀᴛɪᴏɴ. ᴏɴʟʏ ᴄʜᴀᴛ ᴏᴡɴᴇʀꜱ ᴄᴀɴ ᴅᴏ ᴛʜɪꜱ. ᴇᴠᴇʀʏ ᴄʜᴀᴛ ᴄᴀɴ ᴏɴʟʏ ʙᴇ ɪɴ ᴏɴᴇ ꜰᴇᴅᴇʀᴀᴛɪᴏɴ
 ➲ /leavefed <fed_id>: ʟᴇᴀᴠᴇ ᴛʜᴇ ꜰᴇᴅᴇʀᴀᴛɪᴏɴ ɢɪᴠᴇɴ. ᴏɴʟʏ ᴄʜᴀᴛ ᴏᴡɴᴇʀꜱ ᴄᴀɴ ᴅᴏ ᴛʜɪꜱ
 ➲ /setfrules <rules>: ᴀʀʀᴀɴɢᴇ ꜰᴇᴅᴇʀᴀᴛɪᴏɴ ʀᴜʟᴇꜱ
 ➲ /fedadmins: ꜱʜᴏᴡ ꜰᴇᴅᴇʀᴀᴛɪᴏɴ ᴀᴅᴍɪɴ
 ➲ /fbanlist: ᴅɪꜱᴘʟᴀʏꜱ ᴀʟʟ ᴜꜱᴇʀꜱ ᴡʜᴏ ᴀʀᴇ ᴠɪᴄᴛɪᴍɪᴢᴇᴅ ᴀᴛ ᴛʜᴇ ꜰᴇᴅᴇʀᴀᴛɪᴏɴ ᴀᴛ ᴛʜɪꜱ ᴛɪᴍᴇ
 ➲ /fedchats: ɢᴇᴛ ᴀʟʟ ᴛʜᴇ ᴄʜᴀᴛꜱ ᴛʜᴀᴛ ᴀʀᴇ ᴄᴏɴɴᴇᴄᴛᴇᴅ ɪɴ ᴛʜᴇ ꜰᴇᴅᴇʀᴀᴛɪᴏɴ
 ➲ /chatfed : ꜱᴇᴇ ᴛʜᴇ ꜰᴇᴅᴇʀᴀᴛɪᴏɴ ɪɴ ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ᴄʜᴀᴛ
"""

FedOwner = """
𝗙𝗲𝗱 𝗢𝘄𝗻𝗲𝗿 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀:
 ➲ /newfed <fed_name>: ᴄʀᴇᴀᴛᴇꜱ ᴀ ꜰᴇᴅᴇʀᴀᴛɪᴏɴ, ᴏɴᴇ ᴀʟʟᴏᴡᴇᴅ ᴘᴇʀ ᴜꜱᴇʀ
 ➲ /renamefed <fed_id> <new_fed_name>: ʀᴇɴᴀᴍᴇꜱ ᴛʜᴇ ꜰᴇᴅ ɪᴅ ᴛᴏ ᴀ ɴᴇᴡ ɴᴀᴍᴇ
 ➲ /delfed <fed_id>: ᴅᴇʟᴇᴛᴇ ᴀ ꜰᴇᴅᴇʀᴀᴛɪᴏɴ, ᴀɴᴅ ᴀɴʏ ɪɴꜰᴏʀᴍᴀᴛɪᴏɴ ʀᴇʟᴀᴛᴇᴅ ᴛᴏ ɪᴛ. ᴡɪʟʟ ɴᴏᴛ ᴄᴀɴᴄᴇʟ ʙʟᴏᴄᴋᴇᴅ ᴜꜱᴇʀꜱ
 ➲ /fpromote <user>: ᴀꜱꜱɪɢɴꜱ ᴛʜᴇ ᴜꜱᴇʀ ᴀꜱ ᴀ ꜰᴇᴅᴇʀᴀᴛɪᴏɴ ᴀᴅᴍɪɴ. ᴇɴᴀʙʟᴇꜱ ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅꜱ ꜰᴏʀ ᴛʜᴇ ᴜꜱᴇʀ ᴜɴᴅᴇʀ ꜰᴇᴅ ᴀᴅᴍɪɴꜱ
 ➲ /fdemote <user>: ᴅʀᴏᴘꜱ ᴛʜᴇ ᴜꜱᴇʀ ꜰʀᴏᴍ ᴛʜᴇ ᴀᴅᴍɪɴ ꜰᴇᴅᴇʀᴀᴛɪᴏɴ ᴛᴏ ᴀ ɴᴏʀᴍᴀʟ ᴜꜱᴇʀ
 ➲ /subfed <fed_id>: ꜱᴜʙꜱᴄʀɪʙᴇꜱ ᴛᴏ ᴀ ɢɪᴠᴇɴ ꜰᴇᴅ ɪᴅ, ʙᴀɴꜱ ꜰʀᴏᴍ ᴛʜᴀᴛ ꜱᴜʙꜱᴄʀɪʙᴇᴅ ꜰᴇᴅ ᴡɪʟʟ ᴀʟꜱᴏ ʜᴀᴘᴘᴇɴ ɪɴ ʏᴏᴜʀ ꜰᴇᴅ
 ➲ /unsubfed <fed_id>: ᴜɴꜱᴜʙꜱᴄʀɪʙᴇꜱ ᴛᴏ ᴀ ɢɪᴠᴇɴ ꜰᴇᴅ ɪᴅ
 ➲ /setfedlog <fed_id>: ꜱᴇᴛꜱ ᴛʜᴇ ɢʀᴏᴜᴘ ᴀꜱ ᴀ ꜰᴇᴅ ʟᴏɢ ʀᴇᴘᴏʀᴛ ʙᴀꜱᴇ ꜰᴏʀ ᴛʜᴇ ꜰᴇᴅᴇʀᴀᴛɪᴏɴ
 ➲ /unsetfedlog <fed_id>: ʀᴇᴍᴏᴠᴇᴅ ᴛʜᴇ ɢʀᴏᴜᴘ ᴀꜱ ᴀ ꜰᴇᴅ ʟᴏɢ ʀᴇᴘᴏʀᴛ ʙᴀꜱᴇ ꜰᴏʀ ᴛʜᴇ ꜰᴇᴅᴇʀᴀᴛɪᴏɴ
 ➲ /fbroadcast <message>: ʙʀᴏᴀᴅᴄᴀꜱᴛꜱ ᴀ ᴍᴇꜱꜱᴀɢᴇꜱ ᴛᴏ ᴀʟʟ ɢʀᴏᴜᴘꜱ ᴛʜᴀᴛ ʜᴀᴠᴇ ᴊᴏɪɴᴇᴅ ʏᴏᴜʀ ꜰᴇᴅ
 ➲ /fedsubs: ꜱʜᴏᴡꜱ ᴛʜᴇ ꜰᴇᴅꜱ ʏᴏᴜʀ ɢʀᴏᴜᴘ ɪꜱ ꜱᴜʙꜱᴄʀɪʙᴇᴅ ᴛᴏ
"""

IMPORTED = {}
MIGRATEABLE = []
HELPABLE = {}
STATS = []
USER_INFO = []
DATA_IMPORT = []
DATA_EXPORT = []
CHAT_SETTINGS = {}
USER_SETTINGS = {}

for module_name in ALL_MODULES:
    imported_module = importlib.import_module("AltronRobot.modules." + module_name)
    if not hasattr(imported_module, "__mod_name__"):
        imported_module.__mod_name__ = imported_module.__name__

    if imported_module.__mod_name__.lower() not in IMPORTED:
        IMPORTED[imported_module.__mod_name__.lower()] = imported_module
    else:
        raise Exception("Can't have two modules with the same name! Please change one")

    if hasattr(imported_module, "__help__") and imported_module.__help__:
        HELPABLE[imported_module.__mod_name__.lower()] = imported_module

    # Chats to migrate on chat_migrated events
    if hasattr(imported_module, "__migrate__"):
        MIGRATEABLE.append(imported_module)

    if hasattr(imported_module, "__stats__"):
        STATS.append(imported_module)

    if hasattr(imported_module, "__user_info__"):
        USER_INFO.append(imported_module)

    if hasattr(imported_module, "__import_data__"):
        DATA_IMPORT.append(imported_module)

    if hasattr(imported_module, "__export_data__"):
        DATA_EXPORT.append(imported_module)

    if hasattr(imported_module, "__chat_settings__"):
        CHAT_SETTINGS[imported_module.__mod_name__.lower()] = imported_module

    if hasattr(imported_module, "__user_settings__"):
        USER_SETTINGS[imported_module.__mod_name__.lower()] = imported_module


# do not async
def send_help(chat_id, text, keyboard=None):
    if not keyboard:
        keyboard = InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help"))
    dispatcher.bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True,
        reply_markup=keyboard,
    )


@run_async
def start(update: Update, context: CallbackContext):
    args = context.args
    uptime = get_readable_time((time.time() - StartTime))
    if update.effective_chat.type == "private":
        if len(args) >= 1:
            if args[0].lower() == "help":
                send_help(update.effective_chat.id, HELP_STRINGS)
            elif args[0].lower().startswith("ghelp_"):
                mod = args[0].lower().split("_", 1)[1]
                if not HELPABLE.get(mod, False):
                    return
                buttonsf = [[InlineKeyboardButton(text="◁", callback_data="help_back")]]
                if HELPABLE[mod].__mod_name__ == "Fᴇᴅs":
                    buttonsf = [
                        [
                            InlineKeyboardButton(text="ᴏᴡɴᴇʀ ᴄᴏᴍᴍᴀɴᴅꜱ", callback_data="FedOwn"),
                            InlineKeyboardButton(text="ᴀᴅᴍɪɴ ᴄᴏᴍᴍᴀɴᴅꜱ", callback_data="FedAdms")
                        ],
                        [
                            InlineKeyboardButton(text="ᴜꜱᴇʀ ᴄᴏᴍᴍᴀɴᴅꜱ", callback_data="FedUsers")
                        ],
                        [InlineKeyboardButton(text="◁", callback_data="help_back")]
                        ]
                send_help(
                    update.effective_chat.id,
                    HELPABLE[mod].__help__,
                    InlineKeyboardMarkup(buttonsf),
                )

            elif args[0].lower().startswith("stngs_"):
                match = re.match("stngs_(.*)", args[0].lower())
                chat = dispatcher.bot.getChat(match.group(1))

                if is_user_admin(chat, update.effective_user.id):
                    send_settings(match.group(1), update.effective_user.id, False)
                else:
                    send_settings(match.group(1), update.effective_user.id, True)

            elif args[0][1:].isdigit() and "rules" in IMPORTED:
                IMPORTED["rules"].send_rules(update, args[0], from_pm=True)

        else:
            update.effective_message.reply_text(
                PM_START_TEXT.format(BOT_NAME),
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=ParseMode.MARKDOWN,
                timeout=60,
            )
    else:
        update.effective_message.reply_photo(
            START_IMG,
            caption="ɪ ᴀᴍ ᴀʟɪᴠᴇ ʙᴀʙʏ !\n<b>ɪ ᴅɪᴅɴ'ᴛ sʟᴇᴘᴛ sɪɴᴄᴇ​:</b> <code>{}</code>".format(
                uptime
            ),
            parse_mode=ParseMode.HTML,
        )


def error_handler(update, context):
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    LOGGER.error(msg="Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(
        None, context.error, context.error.__traceback__
    )
    tb = "".join(tb_list)

    # Build the message with some markup and additional information about what happened.
    message = (
        "An exception was raised while handling an update\n"
        "<pre>update = {}</pre>\n\n"
        "<pre>{}</pre>"
    ).format(
        html.escape(json.dumps(update.to_dict(), indent=2, ensure_ascii=False)),
        html.escape(tb),
    )

    if len(message) >= 4096:
        message = message[:4096]
    # Finally, send the message
    context.bot.send_message(chat_id=OWNER_ID, text=message, parse_mode=ParseMode.HTML)


# for test purposes
def error_callback(update: Update, context: CallbackContext):
    error = context.error
    try:
        raise error
    except Unauthorized:
        print("no nono1")
        print(error)
        # remove update.message.chat_id from conversation list
    except BadRequest:
        print("no nono2")
        print("BadRequest caught")
        print(error)

        # handle malformed requests - read more below!
    except TimedOut:
        print("no nono3")
        # handle slow connection problems
    except NetworkError:
        print("no nono4")
        # handle other connection problems
    except ChatMigrated as err:
        print("no nono5")
        print(err)
        # the chat_id of a group has changed, use e.new_chat_id instead
    except TelegramError:
        print(error)
        # handle all other telegram related errors


@run_async
def help_button(update, context):
    query = update.callback_query
    mod_match = re.match(r"help_module\((.+?)\)", query.data)
    prev_match = re.match(r"help_prev\((.+?)\)", query.data)
    next_match = re.match(r"help_next\((.+?)\)", query.data)
    back_match = re.match(r"help_back", query.data)

    try:
        if mod_match:
            module = mod_match.group(1)
            text = (
                "» *ᴀᴠᴀɪʟᴀʙʟᴇ ᴄᴏᴍᴍᴀɴᴅs ꜰᴏʀ​​* *{}* :\n".format(
                    HELPABLE[module].__mod_name__
                )
                + HELPABLE[module].__help__
            )
            buttonsf = [[InlineKeyboardButton(text="◁", callback_data="help_back")]]

            if HELPABLE[module].__mod_name__ == "Fᴇᴅs":
                buttonsf = [
                    [
                        InlineKeyboardButton(text="ᴏᴡɴᴇʀ ᴄᴏᴍᴍᴀɴᴅꜱ", callback_data="FedOwn"),
                        InlineKeyboardButton(text="ᴀᴅᴍɪɴ ᴄᴏᴍᴍᴀɴᴅꜱ", callback_data="FedAdms")
                    ],
                    [
                        InlineKeyboardButton(text="ᴜꜱᴇʀ ᴄᴏᴍᴍᴀɴᴅꜱ", callback_data="FedUsers")
                    ],
                    [InlineKeyboardButton(text="◁", callback_data="help_back")]
                    ]

            query.message.edit_text(
                text=text,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup(buttonsf),
            )

        elif prev_match:
            curr_page = int(prev_match.group(1))
            query.message.edit_text(
                text=HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(curr_page - 1, HELPABLE, "help")
                ),
            )

        elif next_match:
            next_page = int(next_match.group(1))
            query.message.edit_text(
                text=HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(next_page + 1, HELPABLE, "help")
                ),
            )

        elif back_match:
            query.message.edit_text(
                text=HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, HELPABLE, "help")
                ),
            )

        context.bot.answer_callback_query(query.id)

    except BadRequest:
        pass



@run_async
def fed_button(update, context):
    query = update.callback_query
    buttonsf = [[InlineKeyboardButton(text="◁", callback_data="help_back")]]

    try:
        if query.data == "FedOwn":
            query.message.edit_text(text=FedOwner, reply_markup=InlineKeyboardMarkup(buttonsf),)

        elif query.data == "FedAdms":
            query.message.edit_text(text=FedAdmins, reply_markup=InlineKeyboardMarkup(buttonsf),)

        elif query.data == "FedUsers":
            query.message.edit_text(text=FedUsers, reply_markup=InlineKeyboardMarkup(buttonsf),)

        context.bot.answer_callback_query(query.id)

    except BadRequest as E:
        print(E)
        # pass


@run_async
def Altron_about_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    if query.data == "altron_":
        query.message.edit_text(
            text=ALTRON_ABOUT,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="✘ sᴜᴩᴩᴏʀᴛ", callback_data="altron_support"
                        ),
                        InlineKeyboardButton(
                            text="✘ ᴄᴏᴍᴍᴀɴᴅs", callback_data="help_back"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text="✘ ᴅᴇᴠᴇʟᴏᴩᴇʀ", url=f"tg://user?id={OWNER_ID}"
                        ),
                        InlineKeyboardButton(
                            text="✘ sᴏᴜʀᴄᴇ",
                            callback_data="source_",
                        ),
                    ],
                    [
                        InlineKeyboardButton(text="◁", callback_data="altron_back"),
                    ],
                ]
            ),
        )
    elif query.data == "altron_support":
        query.message.edit_text(
            text="*๏ ᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ ʙᴜᴛᴛᴏɴs ɢɪᴠᴇɴ ʙᴇʟᴏᴡ ᴛᴏ ɢᴇᴛ ʜᴇʟᴩ ᴀɴᴅ ᴍᴏʀᴇ ɪɴғᴏʀᴍᴀᴛɪᴏɴ ᴀʙᴏᴜᴛ ᴍᴇ.*"
            f"\n\nɪғ ʏᴏᴜ ғᴏᴜɴᴅ ᴀɴʏ ʙᴜɢ ɪɴ {BOT_NAME} ᴏʀ ɪғ ʏᴏᴜ ᴡᴀɴɴᴀ ɢɪᴠᴇ ғᴇᴇᴅʙᴀᴄᴋ ᴀʙᴏᴜᴛ ᴛʜᴇ {BOT_NAME}, ᴩʟᴇᴀsᴇ ʀᴇᴩᴏʀᴛ ɪᴛ ᴀᴛ sᴜᴩᴩᴏʀᴛ ᴄʜᴀᴛ.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="✘ sᴜᴩᴩᴏʀᴛ", url=f"https://t.me/{SUPPORT_CHAT}"
                        ),
                        InlineKeyboardButton(
                            text="✘ ᴜᴩᴅᴀᴛᴇs", url=f"https://t.me/TheAltron"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text="✘ ᴅᴇᴠᴇʟᴏᴩᴇʀ", url=f"tg://user?id={OWNER_ID}"
                        ),
                        InlineKeyboardButton(
                            text="✘ ɢɪᴛʜᴜʙ",
                            url="https://github.com/ItZxSTaR",
                        ),
                    ],
                    [
                        InlineKeyboardButton(text="◁", callback_data="altron_"),
                    ],
                ]
            ),
        )
    elif query.data == "altron_back":
        query.message.edit_text(
            PM_START_TEXT.format(BOT_NAME),
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=ParseMode.MARKDOWN,
            timeout=60,
            disable_web_page_preview=False,
        )


@run_async
def Source_about_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    if query.data == "source_":
        query.message.edit_text(
            text=f"""
*ʜᴇʏ,
 ᴛʜɪs ɪs {BOT_NAME},
ᴀɴ ᴏᴩᴇɴ sᴏᴜʀᴄᴇ ᴛᴇʟᴇɢʀᴀᴍ ɢʀᴏᴜᴩ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ ʙᴏᴛ.*

ᴡʀɪᴛᴛᴇɴ ɪɴ ᴩʏᴛʜᴏɴ ᴡɪᴛʜ ᴛʜᴇ ʜᴇʟᴩ ᴏғ : [ᴛᴇʟᴇᴛʜᴏɴ](https://github.com/LonamiWebs/Telethon)
[ᴩʏʀᴏɢʀᴀᴍ](https://github.com/pyrogram/pyrogram)
[ᴩʏᴛʜᴏɴ-ᴛᴇʟᴇɢʀᴀᴍ-ʙᴏᴛ](https://github.com/python-telegram-bot/python-telegram-bot)
ᴀɴᴅ ᴜsɪɴɢ [sǫʟᴀʟᴄʜᴇᴍʏ](https://www.sqlalchemy.org) ᴀɴᴅ [ᴍᴏɴɢᴏ](https://cloud.mongodb.com) ᴀs ᴅᴀᴛᴀʙᴀsᴇ.


*ʜᴇʀᴇ ɪs ᴍʏ sᴏᴜʀᴄᴇ ᴄᴏᴅᴇ :* [ɢɪᴛʜᴜʙ](https://github.com/ItZxSTaR/AltronRobot)


{BOT_NAME} ɪs ʟɪᴄᴇɴsᴇᴅ ᴜɴᴅᴇʀ ᴛʜᴇ [ᴍɪᴛ ʟɪᴄᴇɴsᴇ](https://github.com/ItZxSTaR/AltronRobot/blob/master/LICENSE).
© 2022 - 2023 [@𝐓ʜᴇ𝐀ʟᴛʀᴏɴ](https://t.me/{SUPPORT_CHAT}), ᴀʟʟ ʀɪɢʜᴛs ʀᴇsᴇʀᴠᴇᴅ.
""",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="◁", callback_data="source_back")]]
            ),
        )
    elif query.data == "source_back":
        query.message.edit_text(
            PM_START_TEXT.format(BOT_NAME),
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=ParseMode.MARKDOWN,
            timeout=60,
            disable_web_page_preview=False,
        )


@run_async
def get_help(update: Update, context: CallbackContext):
    chat = update.effective_chat
    args = update.effective_message.text.split(None, 1)

    # ONLY send help in PM
    if chat.type != chat.PRIVATE:
        if len(args) >= 2 and any(args[1].lower() == x for x in HELPABLE):
            module = args[1].lower()
            update.effective_message.reply_text(
                f"» ᴄᴏɴᴛᴀᴄᴛ ᴍᴇ ɪɴ ᴘᴍ ᴛᴏ ɢᴇᴛ ʜᴇʟᴘ ᴏꜰ {module.capitalize()}",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="• ʜᴇʟᴘ •​",
                                url="t.me/{}?start=ghelp_{}".format(
                                    context.bot.username, module
                                ),
                            )
                        ]
                    ]
                ),
            )
            return
        update.effective_message.reply_text(
            "» ᴄʜᴏᴏsᴇ ᴀɴ ᴏᴩᴛɪᴏɴ ғᴏʀ ɢᴇᴛᴛɪɴɢ ʜᴇʟᴩ.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="• ᴏᴩᴇɴ ɪɴ ᴩʀɪᴠᴀᴛᴇ •",
                            url="https://t.me/{}?start=help".format(
                                context.bot.username
                            ),
                        ),
                        InlineKeyboardButton(
                            text="• ᴏᴩᴇɴ ʜᴇʀᴇ •",
                            callback_data="help_back",
                        )
                    ],
                ]
            ),
        )
        return

    elif len(args) >= 2 and any(args[1].lower() == x for x in HELPABLE):
        module = args[1].lower()
        text = (
            "» ʜᴇʀᴇ ɪꜱ ᴛʜᴇ ᴀᴠᴀɪʟᴀʙʟᴇ ʜᴇʟᴘ ꜰᴏʀ ᴛʜᴇ *{}* ᴍᴏᴅᴜʟᴇ:\n".format(
                HELPABLE[module].__mod_name__
            )
            + HELPABLE[module].__help__
        )
        buttonsf = [[InlineKeyboardButton(text="◁", callback_data="help_back")]]
        if HELPABLE[module].__mod_name__ == "Fᴇᴅs":
            buttonsf = [
                [
                    InlineKeyboardButton(text="ᴏᴡɴᴇʀ ᴄᴏᴍᴍᴀɴᴅꜱ", callback_data="FedOwn"),
                    InlineKeyboardButton(text="ᴀᴅᴍɪɴ ᴄᴏᴍᴍᴀɴᴅꜱ", callback_data="FedAdms")
                ],
                [
                    InlineKeyboardButton(text="ᴜꜱᴇʀ ᴄᴏᴍᴍᴀɴᴅꜱ", callback_data="FedUsers")
                ],
                [InlineKeyboardButton(text="◁", callback_data="help_back")]
                ]
        send_help(
            chat.id,
            text,
            InlineKeyboardMarkup(buttonsf),
        )

    else:
        send_help(chat.id, HELP_STRINGS)


def send_settings(chat_id, user_id, user=False):
    if user:
        if USER_SETTINGS:
            settings = "\n\n".join(
                "*{}*:\n{}".format(mod.__mod_name__, mod.__user_settings__(user_id))
                for mod in USER_SETTINGS.values()
            )
            dispatcher.bot.send_message(
                user_id,
                "» ᴛʜᴇꜱᴇ ᴀʀᴇ ʏᴏᴜʀ ᴄᴜʀʀᴇɴᴛ ꜱᴇᴛᴛɪɴɢꜱ:\n\n" + settings,
                parse_mode=ParseMode.MARKDOWN,
            )

        else:
            dispatcher.bot.send_message(
                user_id,
                "Seems like there aren't any user specific settings available :'(",
                parse_mode=ParseMode.MARKDOWN,
            )

    else:
        if CHAT_SETTINGS:
            chat_name = dispatcher.bot.getChat(chat_id).title
            dispatcher.bot.send_message(
                user_id,
                text="Which module would you like to check {}'s settings for?".format(chat_name),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, CHAT_SETTINGS, "stngs", chat=chat_id)
                ),
            )
        else:
            dispatcher.bot.send_message(
                user_id,
                "Seems like there aren't any chat settings available :'(\nSend this "
                "in a group chat you're admin in to find its current settings!",
                parse_mode=ParseMode.MARKDOWN,
            )


@run_async
def settings_button(update: Update, context: CallbackContext):
    query = update.callback_query
    user = update.effective_user
    bot = context.bot
    mod_match = re.match(r"stngs_module\((.+?),(.+?)\)", query.data)
    prev_match = re.match(r"stngs_prev\((.+?),(.+?)\)", query.data)
    next_match = re.match(r"stngs_next\((.+?),(.+?)\)", query.data)
    back_match = re.match(r"stngs_back\((.+?)\)", query.data)
    try:
        if mod_match:
            chat_id = mod_match.group(1)
            module = mod_match.group(2)
            chat = bot.get_chat(chat_id)
            text = "» *{}* ʜᴀꜱ ᴛʜᴇ ꜰᴏʟʟᴏᴡɪɴɢ ꜱᴇᴛᴛɪɴɢꜱ ꜰᴏʀ ᴛʜᴇ *{}* ᴍᴏᴅᴜʟᴇ:\n\n".format(
                escape_markdown(chat.title), CHAT_SETTINGS[module].__mod_name__
            ) + CHAT_SETTINGS[module].__chat_settings__(chat_id, user.id)
            query.message.reply_text(
                text=text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="◁",
                                callback_data="stngs_back({})".format(chat_id),
                            )
                        ]
                    ]
                ),
            )

        elif prev_match:
            chat_id = prev_match.group(1)
            curr_page = int(prev_match.group(2))
            chat = bot.get_chat(chat_id)
            query.message.reply_text(
                "Hi there! There are quite a few settings for {} - go ahead and pick what "
                "you're interested in.".format(chat.title),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(
                        curr_page - 1, CHAT_SETTINGS, "stngs", chat=chat_id
                    )
                ),
            )

        elif next_match:
            chat_id = next_match.group(1)
            next_page = int(next_match.group(2))
            chat = bot.get_chat(chat_id)
            query.message.reply_text(
                "Hi there! There are quite a few settings for {} - go ahead and pick what "
                "you're interested in.".format(chat.title),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(
                        next_page + 1, CHAT_SETTINGS, "stngs", chat=chat_id
                    )
                ),
            )

        elif back_match:
            chat_id = back_match.group(1)
            chat = bot.get_chat(chat_id)
            query.message.reply_text(
                text="Hi there! There are quite a few settings for {} - go ahead and pick what "
                "you're interested in.".format(escape_markdown(chat.title)),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, CHAT_SETTINGS, "stngs", chat=chat_id)
                ),
            )

        # ensure no spinny white circle
        bot.answer_callback_query(query.id)
        query.message.delete()
    except BadRequest as excp:
        if excp.message not in [
            "Message is not modified",
            "Query_id_invalid",
            "Message can't be deleted",
        ]:
            LOGGER.exception("Exception in settings buttons. %s", str(query.data))


@run_async
def get_settings(update: Update, context: CallbackContext):
    chat = update.effective_chat
    user = update.effective_user
    msg = update.effective_message

    # ONLY send settings in PM
    if chat.type != chat.PRIVATE:
        if is_user_admin(chat, user.id):
            text = "» ᴄʟɪᴄᴋ ʜᴇʀᴇ ᴛᴏ ɢᴇᴛ ᴛʜɪꜱ ᴄʜᴀᴛ'ꜱ ꜱᴇᴛᴛɪɴɢꜱ, ᴀꜱ ᴡᴇʟʟ ᴀꜱ ʏᴏᴜʀꜱ."
            msg.reply_text(
                text,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="sᴇᴛᴛɪɴɢs​",
                                url="t.me/{}?start=stngs_{}".format(
                                    context.bot.username, chat.id
                                ),
                            )
                        ]
                    ]
                ),
            )
        else:
            pass

    else:
        send_settings(chat.id, user.id, True)


@run_async
def donate(update: Update, context: CallbackContext):
    user = update.effective_message.from_user
    chat = update.effective_chat  # type: Optional[Chat]
    bot = context.bot
    if chat.type == "private":
        update.effective_message.reply_text(
            DONATE_STRING, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True
        )

        if OWNER_ID != 1356469075 and DONATION_LINK:
            update.effective_message.reply_text(
                f"» ᴛʜᴇ ᴅᴇᴠᴇʟᴏᴩᴇʀ ᴏғ {BOT_NAME} sᴏʀᴄᴇ ᴄᴏᴅᴇ ɪs [ᴘʏᴛʜᴏɴ](https://t.me/ItzExStar)."
                f"\n\nʙᴜᴛ ʏᴏᴜ ᴄᴀɴ ᴀʟsᴏ ᴅᴏɴᴀᴛᴇ ᴛᴏ ᴛʜᴇ ᴩᴇʀsᴏɴ ᴄᴜʀʀᴇɴᴛʟʏ ʀᴜɴɴɪɴɢ ᴍᴇ : [ʜᴇʀᴇ]({DONATION_LINK})",
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
            )

    else:
        try:
            bot.send_message(
                user.id,
                DONATE_STRING,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
            )

            update.effective_message.reply_text(
                "I've PM'ed you about donating to my creator!"
            )
        except Unauthorized:
            update.effective_message.reply_text(
                "Contact me in PM first to get donation information."
            )


def migrate_chats(update: Update, context: CallbackContext):
    msg = update.effective_message
    if msg.migrate_to_chat_id:
        old_chat = update.effective_chat.id
        new_chat = msg.migrate_to_chat_id
    elif msg.migrate_from_chat_id:
        old_chat = msg.migrate_from_chat_id
        new_chat = update.effective_chat.id
    else:
        return

    LOGGER.info("Migrating from %s, to %s", str(old_chat), str(new_chat))
    for mod in MIGRATEABLE:
        mod.__migrate__(old_chat, new_chat)

    LOGGER.info("Successfully migrated!")
    raise DispatcherHandlerStop


def main():

    if SUPPORT_CHAT is not None and isinstance(SUPPORT_CHAT, str):
        try:
            dispatcher.bot.send_photo(
                f"@{SUPPORT_CHAT}",
                photo=START_IMG,
                caption=f"""
ㅤ🥀 {BOT_NAME} ɪs ᴀʟɪᴠᴇ...

┏•❅────✧❅✦❅✧────❅•┓
ㅤ★ **ᴘʏᴛʜᴏɴ :** `{y()}`
ㅤ★ **ʟɪʙʀᴀʀʏ :** `{telever}`
ㅤ★ **ᴛᴇʟᴇᴛʜᴏɴ :** `{tlhver}`
ㅤ★ **ᴩʏʀᴏɢʀᴀᴍ :** `{pyrover}`
┗•❅────✧❅✦❅✧────❅•┛""",
                parse_mode=ParseMode.MARKDOWN,
            )
        except Unauthorized:
            LOGGER.warning(
                f"Bot isn't able to send message to @{SUPPORT_CHAT}, go and check!"
            )
        except BadRequest as e:
            LOGGER.warning(e.message)

    start_handler = CommandHandler("start", start)

    help_handler = CommandHandler("help", get_help)
    help_callback_handler = CallbackQueryHandler(help_button, pattern=r"help_.*")
    fed_callback_handler = CallbackQueryHandler(fed_button, pattern=r"Fed")

    settings_handler = CommandHandler("settings", get_settings)
    settings_callback_handler = CallbackQueryHandler(settings_button, pattern=r"stngs_")

    about_callback_handler = CallbackQueryHandler(
        Altron_about_callback, pattern=r"altron_"
    )
    source_callback_handler = CallbackQueryHandler(
        Source_about_callback, pattern=r"source_"
    )

    donate_handler = CommandHandler("donate", donate)
    migrate_handler = MessageHandler(Filters.status_update.migrate, migrate_chats)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(about_callback_handler)
    dispatcher.add_handler(source_callback_handler)
    dispatcher.add_handler(settings_handler)
    dispatcher.add_handler(help_callback_handler)
    dispatcher.add_handler(fed_callback_handler)
    dispatcher.add_handler(settings_callback_handler)
    dispatcher.add_handler(migrate_handler)
    dispatcher.add_handler(donate_handler)

    dispatcher.add_error_handler(error_callback)

    if WEBHOOK:
        LOGGER.info("Using webhooks.")
        updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN)

        if CERT_PATH:
            updater.bot.set_webhook(url=URL + TOKEN, certificate=open(CERT_PATH, "rb"))
        else:
            updater.bot.set_webhook(url=URL + TOKEN)

    else:
        LOGGER.info("Using long polling.")
        updater.start_polling(timeout=15, read_latency=4, clean=True)

    if len(argv) not in (1, 3, 4):
        telethn.disconnect()
    else:
        telethn.run_until_disconnected()

    updater.idle()


if __name__ == "__main__":
    LOGGER.info("Successfully loaded modules: " + str(ALL_MODULES))
    telethn.start(bot_token=TOKEN)
    pbot.start()
    main()
