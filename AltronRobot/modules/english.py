import json

import requests
from PyDictionary import PyDictionary
from telethon import *
from telethon.tl.types import *

from AltronRobot.events import register

API_KEY = "6ae0c3a0-afdc-4532-a810-82ded0054236"
URL = "http://services.gingersoftware.com/Ginger/correct/json/GingerTheText"


@register(pattern="^/spell(?: |$)(.*)")
async def _(event):
    msg = event.text.split(" ", 1)[1]
    params = dict(lang="US", clientVersion="2.0", apiKey=API_KEY, text=msg)

    res = requests.get(URL, params=params)
    changes = json.loads(res.text).get("LightGingerTheTextResult")
    curr_string = ""
    prev_end = 0

    for change in changes:
        start = change.get("From")
        end = change.get("To") + 1
        suggestions = change.get("Suggestions")
        if suggestions:
            sugg_str = suggestions[0].get("Text")
            curr_string += msg[prev_end:start] + sugg_str
            prev_end = end

    curr_string += msg[prev_end:]
    await event.reply(curr_string)


dictionary = PyDictionary()

@register(pattern="^/define")
async def _(event):
    text = event.text.split(" ", 1)[1]
    let = dictionary.meaning(f"{text}")
    X = (str(let['Noun'])[1:-2].replace("'", "")).capitalize()
    AltPy = f"» ᴍᴇᴀɴɪɴɢ ᴏꜰ {text}:\n - `{X}`"
    await event.reply(AltPy)


@register(pattern="^/synonyms")
async def _(event):
    text = event.text.split(" ", 1)[1]
    synonyms = dictionary.synonym(f"{text}")
    AltPy = f"» ꜱʏɴᴏɴʏᴍꜱ ᴏꜰ {text}:\n"
    for Syn in synonyms.split(""):
        AltPy += f" - {Syn}"
    await event.reply(AltPy)


@register(pattern="^/antonyms")
async def _(event):
    text = event.text.split(" ", 1)[1]
    antonyms = dictionary.antonym(f"{text}")
    AltPy = f"» ᴀɴᴛᴏɴʏᴍꜱ ᴏꜰ {text}:\n"
    for Ant in antonyms:
        AltPy += f" - {Ant}"
    await event.reply(AltPy)


__help__ = f"""
  ➲ /define <text> : ᴛʏᴘᴇ ᴛʜᴇ ᴡᴏʀᴅ ᴏʀ ᴇxᴘʀᴇꜱꜱɪᴏɴ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ꜱᴇᴀʀᴄʜ
     ‣ **For example**: /define kill
  ➲ /spell : ᴡʜɪʟᴇ ʀᴇᴘʟʏɪɴɢ ᴛᴏ ᴀ ᴍᴇꜱꜱᴀɢᴇ, ᴡɪʟʟ ʀᴇᴘʟʏ ᴡɪᴛʜ ᴀ ɢʀᴀᴍᴍᴀʀ ᴄᴏʀʀᴇᴄᴛᴇᴅ ᴠᴇʀꜱɪᴏɴ
  ➲ /synonyms <word> : ꜰɪɴᴅ ᴛʜᴇ ꜱʏɴᴏɴʏᴍꜱ ᴏꜰ ᴀ ᴡᴏʀᴅ
  ➲ /antonyms <word> : ꜰɪɴᴅ ᴛʜᴇ ᴀɴᴛᴏɴʏᴍꜱ ᴏꜰ ᴀ ᴡᴏʀᴅ
"""

__mod_name__ = "Eɴɢʟɪsʜ"
