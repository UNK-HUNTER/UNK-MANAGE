import html
import json
import os
from typing import Optional

from telegram import ParseMode, TelegramError, Update
from telegram.ext import CallbackContext, CommandHandler, run_async
from telegram.utils.helpers import mention_html

from AltronRobot import (
    DEMONS,
    DEV_USERS,
    DRAGONS,
    OWNER_ID,
    SUPPORT_CHAT,
    TIGERS,
    WOLVES,
    dispatcher,
)
from AltronRobot.modules.helper_funcs.chat_status import (
    dev_plus,
    sudo_plus,
    whitelist_plus,
)
from AltronRobot.modules.helper_funcs.extraction import extract_user
from AltronRobot.modules.channel import gloggable

ELEVATED_USERS_FILE = os.path.join(os.getcwd(), "AltronRobot/elevated_users.json")


def check_user_id(user_id: int, context: CallbackContext) -> Optional[str]:
    bot = context.bot
    if not user_id:
        reply = "That...is a chat! baka ka omae?"

    elif user_id == bot.id:
        reply = "This does not work that way."

    else:
        reply = None
    return reply


@run_async
@dev_plus
@gloggable
def addsudo(update: Update, context: CallbackContext) -> str:
    message = update.effective_message
    bot, args = context.bot, context.args
    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)
    rt = ""

    reply = check_user_id(user_id, bot)
    if reply:
        message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE, "r") as infile:
        data = json.load(infile)

    if user_id in DRAGONS:
        message.reply_text("This member is already a Dragon Disaster")
        return ""

    if user_id in DEMONS:
        rt += "Requested HA to promote a Demon Disaster to Dragon."
        data["supports"].remove(user_id)
        DEMONS.remove(user_id)

    if user_id in WOLVES:
        rt += "Requested HA to promote a Wolf Disaster to Dragon."
        data["whitelists"].remove(user_id)
        WOLVES.remove(user_id)

    data["sudos"].append(user_id)
    DRAGONS.append(user_id)

    with open(ELEVATED_USERS_FILE, "w") as outfile:
        json.dump(data, outfile, indent=4)

    update.effective_message.reply_text(
        rt + "\nSuccessfully set Disaster level of {} to Dragon!".format(user_member.first_name)
    )

    return ""


@run_async
@sudo_plus
@gloggable
def addsupport(update: Update, context: CallbackContext,) -> str:
    message = update.effective_message
    bot, args = context.bot, context.args
    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)
    rt = ""

    reply = check_user_id(user_id, bot)
    if reply:
        message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE, "r") as infile:
        data = json.load(infile)

    if user_id in DRAGONS:
        rt += "Requested HA to demote this Dragon to Demon"
        data["sudos"].remove(user_id)
        DRAGONS.remove(user_id)

    if user_id in DEMONS:
        message.reply_text("This user is already a Demon Disaster.")
        return ""

    if user_id in WOLVES:
        rt += "Requested HA to promote this Wolf Disaster to Demon"
        data["whitelists"].remove(user_id)
        WOLVES.remove(user_id)

    data["supports"].append(user_id)
    DEMONS.append(user_id)

    with open(ELEVATED_USERS_FILE, "w") as outfile:
        json.dump(data, outfile, indent=4)

    update.effective_message.reply_text(rt + f"\n{user_member.first_name} was added as a Demon Disaster!")

    return ""


@run_async
@sudo_plus
@gloggable
def addwhitelist(update: Update, context: CallbackContext) -> str:
    message = update.effective_message
    bot, args = context.bot, context.args
    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)
    rt = ""

    reply = check_user_id(user_id, bot)
    if reply:
        message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE, "r") as infile:
        data = json.load(infile)

    if user_id in DRAGONS:
        rt += "This member is a Dragon Disaster, Demoting to Wolf."
        data["sudos"].remove(user_id)
        DRAGONS.remove(user_id)

    if user_id in DEMONS:
        rt += "This user is already a Demon Disaster, Demoting to Wolf."
        data["supports"].remove(user_id)
        DEMONS.remove(user_id)

    if user_id in WOLVES:
        message.reply_text("This user is already a Wolf Disaster.")
        return ""

    data["whitelists"].append(user_id)
    WOLVES.append(user_id)

    with open(ELEVATED_USERS_FILE, "w") as outfile:
        json.dump(data, outfile, indent=4)

    update.effective_message.reply_text(
        rt + f"\nSuccessfully promoted {user_member.first_name} to a Wolf Disaster!"
    )

    return ""


@run_async
@sudo_plus
@gloggable
def addtiger(update: Update, context: CallbackContext) -> str:
    message = update.effective_message
    bot, args = context.bot, context.args
    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)
    rt = ""

    reply = check_user_id(user_id, bot)
    if reply:
        message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE, "r") as infile:
        data = json.load(infile)

    if user_id in DRAGONS:
        rt += "This member is a Dragon Disaster, Demoting to Tiger."
        data["sudos"].remove(user_id)
        DRAGONS.remove(user_id)

    if user_id in DEMONS:
        rt += "This user is already a Demon Disaster, Demoting to Tiger."
        data["supports"].remove(user_id)
        DEMONS.remove(user_id)

    if user_id in WOLVES:
        rt += "This user is already a Wolf Disaster, Demoting to Tiger."
        data["whitelists"].remove(user_id)
        WOLVES.remove(user_id)

    if user_id in TIGERS:
        message.reply_text("This user is already a Tiger.")
        return ""

    data["tigers"].append(user_id)
    TIGERS.append(user_id)

    with open(ELEVATED_USERS_FILE, "w") as outfile:
        json.dump(data, outfile, indent=4)

    update.effective_message.reply_text(
        rt + f"\nSuccessfully promoted {user_member.first_name} to a Tiger Disaster!"
    )

    return ""


@run_async
@dev_plus
@gloggable
def removesudo(update: Update, context: CallbackContext) -> str:
    message = update.effective_message
    bot, args = context.bot, context.args
    user_id = extract_user(message, args)

    reply = check_user_id(user_id, bot)
    if reply:
        message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE, "r") as infile:
        data = json.load(infile)

    if user_id in DRAGONS:
        message.reply_text("Requested HA to demote this user to Civilian")
        DRAGONS.remove(user_id)
        data["sudos"].remove(user_id)

        with open(ELEVATED_USERS_FILE, "w") as outfile:
            json.dump(data, outfile, indent=4)
        return ""

    else:
        message.reply_text("This user is not a Dragon Disaster!")
        return ""


@run_async
@sudo_plus
@gloggable
def removesupport(update: Update, context: CallbackContext) -> str:
    message = update.effective_message
    bot, args = context.bot, context.args
    user_id = extract_user(message, args)

    reply = check_user_id(user_id, bot)
    if reply:
        message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE, "r") as infile:
        data = json.load(infile)

    if user_id in DEMONS:
        message.reply_text("Requested HA to demote this user to Civilian")
        DEMONS.remove(user_id)
        data["supports"].remove(user_id)

        with open(ELEVATED_USERS_FILE, "w") as outfile:
            json.dump(data, outfile, indent=4)
        return ""

    else:
        message.reply_text("This user is not a Demon level Disaster!")
        return ""


@run_async
@sudo_plus
@gloggable
def removewhitelist(update: Update, context: CallbackContext) -> str:
    message = update.effective_message
    bot, args = context.bot, context.args
    user_id = extract_user(message, args)

    reply = check_user_id(user_id, bot)
    if reply:
        message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE, "r") as infile:
        data = json.load(infile)

    if user_id in WOLVES:
        message.reply_text("Demoting to normal user")
        WOLVES.remove(user_id)
        data["whitelists"].remove(user_id)

        with open(ELEVATED_USERS_FILE, "w") as outfile:
            json.dump(data, outfile, indent=4)
        return ""
    else:
        message.reply_text("This user is not a Wolf Disaster!")
        return ""


@run_async
@sudo_plus
@gloggable
def removetiger(update: Update, context: CallbackContext) -> str:
    message = update.effective_message
    bot, args = context.bot, context.args
    user_id = extract_user(message, args)

    reply = check_user_id(user_id, bot)
    if reply:
        message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE, "r") as infile:
        data = json.load(infile)

    if user_id in TIGERS:
        message.reply_text("Demoting to normal user")
        TIGERS.remove(user_id)
        data["tigers"].remove(user_id)

        with open(ELEVATED_USERS_FILE, "w") as outfile:
            json.dump(data, outfile, indent=4)
        return ""
    else:
        message.reply_text("This user is not a Tiger Disaster!")
        return ""


@run_async
@whitelist_plus
def whitelistlist(update: Update, context: CallbackContext):
    reply = "<b>» Known Wolf Disasters 🐺:</b>\n"
    m = update.effective_message.reply_text(
        "» <code>ɢᴀᴛʜᴇʀɪɴɢ ɪɴᴛᴇʟ...</code>", parse_mode=ParseMode.HTML
    )
    bot = context.bot
    for each_user in WOLVES:
        user_id = int(each_user)
        try:
            user = bot.get_chat(user_id)

            reply += f"• {mention_html(user_id, html.escape(user.first_name))}\n"
        except TelegramError:
            pass
    m.edit_text(reply, parse_mode=ParseMode.HTML)


@run_async
@whitelist_plus
def tigerlist(update: Update, context: CallbackContext):
    reply = "<b>» Known Tiger Disasters 🐯:</b>\n"
    m = update.effective_message.reply_text(
        "<code>Gathering intel..</code>", parse_mode=ParseMode.HTML
    )
    bot = context.bot
    for each_user in TIGERS:
        user_id = int(each_user)
        try:
            user = bot.get_chat(user_id)
            reply += f"• {mention_html(user_id, html.escape(user.first_name))}\n"
        except TelegramError:
            pass
    m.edit_text(reply, parse_mode=ParseMode.HTML)


@run_async
@whitelist_plus
def supportlist(update: Update, context: CallbackContext):
    bot = context.bot
    m = update.effective_message.reply_text(
        "» <code>ɢᴀᴛʜᴇʀɪɴɢ ɪɴᴛᴇʟ...</code>", parse_mode=ParseMode.HTML
    )
    reply = "<b>» Known Demon Disasters 👹:</b>\n"
    for each_user in DEMONS:
        user_id = int(each_user)
        try:
            user = bot.get_chat(user_id)
            reply += f"• {mention_html(user_id, html.escape(user.first_name))}\n"
        except TelegramError:
            pass
    m.edit_text(reply, parse_mode=ParseMode.HTML)


@run_async
@whitelist_plus
def sudolist(update: Update, context: CallbackContext):
    bot = context.bot
    m = update.effective_message.reply_text(
        "» <code>ɢᴀᴛʜᴇʀɪɴɢ ɪɴᴛᴇʟ...</code>", parse_mode=ParseMode.HTML
    )
    true_sudo = list(set(DRAGONS) - set(DEV_USERS))
    reply = "<b>» Known Dragon Disasters 🐉:</b>\n"
    for each_user in true_sudo:
        user_id = int(each_user)
        try:
            user = bot.get_chat(user_id)
            reply += f"• {mention_html(user_id, html.escape(user.first_name))}\n"
        except TelegramError:
            pass
    m.edit_text(reply, parse_mode=ParseMode.HTML)


@run_async
@whitelist_plus
def devlist(update: Update, context: CallbackContext):
    bot = context.bot
    m = update.effective_message.reply_text(
        "» <code>ɢᴀᴛʜᴇʀɪɴɢ ɪɴᴛᴇʟ...</code>", parse_mode=ParseMode.HTML
    )
    true_dev = list(set(DEV_USERS) - {OWNER_ID})
    reply = "<b>» Altron Association Members ⚡️:</b>\n"
    for each_user in true_dev:
        user_id = int(each_user)
        try:
            user = bot.get_chat(user_id)
            reply += f"• {mention_html(user_id, html.escape(user.first_name))}\n"
        except TelegramError:
            pass
    m.edit_text(reply, parse_mode=ParseMode.HTML)


__help__ = f"""
**⚠️ Notice:**
  ‣ ᴄᴏᴍᴍᴀɴᴅꜱ ʟɪꜱᴛᴇᴅ ʜᴇʀᴇ ᴏɴʟʏ ᴡᴏʀᴋ ꜰᴏʀ ᴜꜱᴇʀꜱ ᴡɪᴛʜ ꜱᴘᴇᴄɪᴀʟ ᴀᴄᴄᴇꜱꜱ ᴀʀᴇ ᴍᴀɪɴʟʏ ᴜꜱᴇᴅ ꜰᴏʀ ᴛʀᴏᴜʙʟᴇꜱʜᴏᴏᴛɪɴɢ, ᴅᴇʙᴜɢɢɪɴɢ ᴘᴜʀᴘᴏꜱᴇꜱ.
  ‣ ɢʀᴏᴜᴘ ᴀᴅᴍɪɴꜱ/ɢʀᴏᴜᴘ ᴏᴡɴᴇʀꜱ ᴅᴏ ɴᴏᴛ ɴᴇᴇᴅ ᴛʜᴇꜱᴇ ᴄᴏᴍᴍᴀɴᴅꜱ.

𝗟𝗶𝘀𝘁 𝗮𝗹𝗹 𝘀𝗽𝗲𝗰𝗶𝗮𝗹 𝘂𝘀𝗲𝗿𝘀:
  ➲ /dragons : ʟɪꜱᴛꜱ ᴀʟʟ ᴅʀᴀɢᴏɴ ᴅɪꜱᴀꜱᴛᴇʀꜱ
  ➲ /demons : ʟɪꜱᴛꜱ ᴀʟʟ ᴅᴇᴍᴏɴ ᴅɪꜱᴀꜱᴛᴇʀꜱ
  ➲ /tigers : ʟɪꜱᴛꜱ ᴀʟʟ ᴛɪɢᴇʀꜱ ᴅɪꜱᴀꜱᴛᴇʀꜱ
  ➲ /wolves : ʟɪꜱᴛꜱ ᴀʟʟ ᴡᴏʟꜰ ᴅɪꜱᴀꜱᴛᴇʀꜱ
  ➲ /altrons : ʟɪꜱᴛꜱ ᴀʟʟ ᴀʟᴛʀᴏɴ ᴀꜱꜱᴏᴄɪᴀᴛɪᴏɴ ᴍᴇᴍʙᴇʀꜱ
  ➲ /adddragon : ᴀᴅᴅꜱ ᴀ ᴜꜱᴇʀ ᴛᴏ ᴅʀᴀɢᴏɴ
  ➲ /adddemon : ᴀᴅᴅꜱ ᴀ ᴜꜱᴇʀ ᴛᴏ ᴅᴇᴍᴏɴ
  ➲ /addtiger : ᴀᴅᴅꜱ ᴀ ᴜꜱᴇʀ ᴛᴏ ᴛɪɢᴇʀ
  ➲ /addwolf : ᴀᴅᴅꜱ ᴀ ᴜꜱᴇʀ ᴛᴏ ᴡᴏʟꜰ
 ‣ `ᴀᴅᴅ ᴅᴇᴠ ᴅᴏᴇꜱɴᴛ ᴇxɪꜱᴛ, ᴅᴇᴠꜱ ꜱʜᴏᴜʟᴅ ᴋɴᴏᴡ ʜᴏᴡ ᴛᴏ ᴀᴅᴅ ᴛʜᴇᴍꜱᴇʟᴠᴇꜱ`

𝗣𝗶𝗻𝗴:
  ➲ /ping : ɢᴇᴛꜱ ᴘɪɴɢ ᴛɪᴍᴇ ᴏꜰ ʙᴏᴛ ᴛᴏ ᴛᴇʟᴇɢʀᴀᴍ ꜱᴇʀᴠᴇʀ

𝗕𝗿𝗼𝗮𝗱𝗰𝗮𝘀𝘁: **(Bot Owner Only)**
**⚠️ Note:** ᴛʜɪꜱ ꜱᴜᴘᴘᴏʀᴛꜱ ʙᴀꜱɪᴄ ᴍᴀʀᴋᴅᴏᴡɴ
  ➲ /gcast : ʙʀᴏᴀᴅᴄᴀꜱᴛꜱ ᴇᴠᴇʀʏᴡʜᴇʀᴇ
  ➲ /gcast -user : ʙʀᴏᴀᴅᴄᴀꜱᴛꜱ ᴛᴏᴏ ᴀʟʟ ᴜꜱᴇʀꜱ
  ➲ /gcast -chat : ʙʀᴏᴀᴅᴄᴀꜱᴛꜱ ᴛᴏᴏ ᴀʟʟ ɢʀᴏᴜᴘꜱ

𝗚𝗿𝗼𝘂𝗽𝘀 𝗜𝗻𝗳𝗼:
  ➲ /groups : ʟɪꜱᴛ ᴛʜᴇ ɢʀᴏᴜᴘꜱ ᴡɪᴛʜ ɴᴀᴍᴇ, ɪᴅ, ᴍᴇᴍʙᴇʀꜱ ᴄᴏᴜɴᴛ ᴀꜱ ᴀ ᴛxᴛ
  ➲ /leave <ID> : ʟᴇᴀᴠᴇ ᴛʜᴇ ɢʀᴏᴜᴘ, ɪᴅ ᴍᴜꜱᴛ ʜᴀᴠᴇ ʜʏᴘʜᴇɴ
  ➲ /stats : ꜱʜᴏᴡꜱ ᴏᴠᴇʀᴀʟʟ ʙᴏᴛ ꜱᴛᴀᴛꜱ
  ➲ /getchats : ɢᴇᴛꜱ ᴀ ʟɪꜱᴛ ᴏꜰ ɢʀᴏᴜᴘ ɴᴀᴍᴇꜱ ᴛʜᴇ ᴜꜱᴇʀ ʜᴀꜱ ʙᴇᴇɴ ꜱᴇᴇɴ ɪɴ. (ʙᴏᴛ ᴏᴡɴᴇʀ ᴏɴʟʏ)
  ➲ /ginfo username/link/ID : ᴘᴜʟʟꜱ ɪɴꜰᴏ ᴘᴀɴᴇʟ ꜰᴏʀ ᴇɴᴛɪʀᴇ ɢʀᴏᴜᴘ

𝗔𝗰𝗰𝗲𝘀𝘀 𝗰𝗼𝗻𝘁𝗿𝗼𝗹:
  ➲ /lockdown <off/on> : ᴛᴏɢɢʟᴇꜱ ʙᴏᴛ ᴀᴅᴅɪɴɢ ᴛᴏ ɢʀᴏᴜᴘꜱ

𝗦𝗽𝗲𝗲𝗱𝗧𝗲𝘀𝘁:
  ➲ /speedtest : ʀᴜɴꜱ ᴀ ꜱᴘᴇᴇᴅᴛᴇꜱᴛ ᴀɴᴅ ɢɪᴠᴇꜱ ʏᴏᴜ ᴏᴘᴛɪᴏɴꜱ ᴛᴏ ᴄʜᴏᴏꜱᴇ ꜰʀᴏᴍ, ᴛᴇxᴛ ᴏʀ ɪᴍᴀɢᴇ ᴏᴜᴛᴘᴜᴛ

𝗠𝗼𝗱𝘂𝗹𝗲 𝗹𝗼𝗮𝗱𝗶𝗻𝗴:
  ➲ /listmodules : ʟɪꜱᴛꜱ ɴᴀᴍᴇꜱ ᴏꜰ ᴀʟʟ ᴍᴏᴅᴜʟᴇꜱ
  ➲ /load modulename : ʟᴏᴀᴅꜱ ᴛʜᴇ ꜱᴀɪᴅ ᴍᴏᴅᴜʟᴇ ᴛᴏ ᴍᴇᴍᴏʀʏ ᴡɪᴛʜᴏᴜᴛ ʀᴇꜱᴛᴀʀᴛɪɴɢ.
  ➲ /unload modulename : ʟᴏᴀᴅꜱ ᴛʜᴇ ꜱᴀɪᴅ ᴍᴏᴅᴜʟᴇ ꜰʀᴏᴍ ᴍᴇᴍᴏʀʏ ᴡɪᴛʜᴏᴜᴛ ʀᴇꜱᴛᴀʀᴛɪɴɢ ᴛʜᴇ ʙᴏᴛ

𝗥𝗲𝗺𝗼𝘁𝗲 𝗰𝗼𝗺𝗺𝗮𝗻𝗱𝘀:
  ➲ /rban <Id> <Chat-Id> : user group : ʀᴇᴍᴏᴛᴇ ʙᴀɴ
  ➲ /runban : user group : ʀᴇᴍᴏᴛᴇ ᴜɴ-ʙᴀɴ
  ➲ /rpunch : user group : ʀᴇᴍᴏᴛᴇ ᴘᴜɴᴄʜ
  ➲ /rmute : user group : ʀᴇᴍᴏᴛᴇ ᴍᴜᴛᴇ
  ➲ /runmute : user group : ʀᴇᴍᴏᴛᴇ ᴜɴ-ᴍᴜᴛᴇ

𝗪𝗶𝗻𝗱𝗼𝘄𝘀 𝘀𝗲𝗹𝗳 𝗵𝗼𝘀𝘁𝗲𝗱 𝗼𝗻𝗹𝘆:
  ➲ /reboot : ʀᴇꜱᴛᴀʀᴛꜱ ᴛʜᴇ ʙᴏᴛꜱ ꜱᴇʀᴠɪᴄᴇ
  ➲ /gitpull : ᴘᴜʟʟꜱ ᴛʜᴇ ʀᴇᴘᴏ ᴀɴᴅ ᴛʜᴇɴ ʀᴇꜱᴛᴀʀᴛꜱ ᴛʜᴇ ʙᴏᴛꜱ ꜱᴇʀᴠɪᴄᴇ

𝗖𝗵𝗮𝘁𝗯𝗼𝘁:
  ➲ /listaichats : ʟɪꜱᴛꜱ ᴛʜᴇ ᴄʜᴀᴛꜱ ᴛʜᴇ ᴄʜᴀᴛᴍᴏᴅᴇ ɪꜱ ᴇɴᴀʙʟᴇᴅ ɪɴ

𝗗𝗲𝗯𝘂𝗴𝗴𝗶𝗻𝗴 𝗮𝗻𝗱 𝗦𝗵𝗲𝗹𝗹:
  ➲ /debug <on/off> : ʟᴏɢꜱ ᴄᴏᴍᴍᴀɴᴅꜱ ᴛᴏ ᴜᴘᴅᴀᴛᴇꜱ.ᴛxᴛ
  ➲ /logs : ʀᴜɴ ᴛʜɪꜱ ɪɴ ꜱᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ ᴛᴏ ɢᴇᴛ ʟᴏɢꜱ ɪɴ ᴘᴍ
  ➲ /eval : ꜱᴇʟꜰ ᴇxᴘʟᴀɴᴀᴛᴏʀʏ
  ➲ /sh : ʀᴜɴꜱ ꜱʜᴇʟʟ ᴄᴏᴍᴍᴀɴᴅ
  ➲ /clearlocals : ᴀꜱ ᴛʜᴇ ɴᴀᴍᴇ ɢᴏᴇꜱ
  ➲ /dbcleanup : ʀᴇᴍᴏᴠᴇꜱ ᴅᴇʟᴇᴛᴇᴅ ᴀᴄᴄꜱ ᴀɴᴅ ɢʀᴏᴜᴘꜱ ꜰʀᴏᴍ ᴅʙ
  ➲ /py : ʀᴜɴꜱ ᴘʏᴛʜᴏɴ ᴄᴏᴅᴇ
 
𝗚𝗹𝗼𝗯𝗮𝗹 𝗕𝗮𝗻𝘀:
  ➲ /gban <id> <reason> : ɢʙᴀɴꜱ ᴛʜᴇ ᴜꜱᴇʀ, ᴡᴏʀᴋꜱ ʙʏ ʀᴇᴘʟʏ ᴛᴏᴏ
  ➲ /ungban : ᴜɴɢʙᴀɴꜱ ᴛʜᴇ ᴜꜱᴇʀ, ꜱᴀᴍᴇ ᴜꜱᴀɢᴇ ᴀꜱ ɢʙᴀɴ
  ➲ /gbanlist : ᴏᴜᴛᴘᴜᴛꜱ ᴀ ʟɪꜱᴛ ᴏꜰ ɢʙᴀɴɴᴇᴅ ᴜꜱᴇʀꜱ

𝗚𝗹𝗼𝗯𝗮𝗹 𝗕𝗹𝘂𝗲 𝗧𝗲𝘅𝘁:
  ➲ /gignoreblue : <word> : ɢʟᴏʙᴀʟʟʏ ɪɢɴᴏʀᴇ ʙʟᴜᴇᴛᴇxᴛ ᴄʟᴇᴀɴɪɴɢ ᴏꜰ ꜱᴀᴠᴇᴅ ᴡᴏʀᴅ ᴀᴄʀᴏꜱꜱ ᴀʟᴛʀᴏɴ ʀᴏʙᴏᴛ.
  ➲ /ungignoreblue : <word> : ʀᴇᴍᴏᴠᴇ ꜱᴀɪᴅ ᴄᴏᴍᴍᴀɴᴅ ꜰʀᴏᴍ ɢʟᴏʙᴀʟ ᴄʟᴇᴀɴɪɴɢ ʟɪꜱᴛ

**The Altron**
𝗢𝘄𝗻𝗲𝗿 𝗼𝗻𝗹𝘆:
  ➲ /send : <module name> : ꜱᴇɴᴅ ᴍᴏᴅᴜʟᴇ
  ➲ /install : <reply to a .py> : ɪɴꜱᴛᴀʟʟ ᴍᴏᴅᴜʟᴇ

**Heroku Settings**
𝗢𝘄𝗻𝗲𝗿 𝗼𝗻𝗹𝘆:
  ➲ /usage : ᴄʜᴇᴄᴋ ʏᴏᴜʀ ʜᴇʀᴏᴋᴜ ᴅʏɴᴏ ʜᴏᴜʀꜱ ʀᴇᴍᴀɪɴɪɴɢ.
  ➲ /see var <var> : ɢᴇᴛ ʏᴏᴜʀ ᴇxɪꜱᴛɪɴɢ ᴠᴀʀɪʙʟᴇꜱ, ᴜꜱᴇ ɪᴛ ᴏɴʟʏ ᴏɴ ʏᴏᴜʀ ᴘʀɪᴠᴀᴛᴇ ɢʀᴏᴜᴘ!
  ➲ /set var <newvar> <vavariable> : ᴀᴅᴅ ɴᴇᴡ ᴠᴀʀɪᴀʙʟᴇ ᴏʀ ᴜᴘᴅᴀᴛᴇ ᴇxɪꜱᴛɪɴɢ ᴠᴀʟᴜᴇ ᴠᴀʀɪᴀʙʟᴇ.
  ➲ /del var <var> : ᴅᴇʟᴇᴛᴇ ᴇxɪꜱᴛɪɴɢ ᴠᴀʀɪᴀʙʟᴇ.
  ➲ /logs : ɢᴇᴛ ʜᴇʀᴏᴋᴜ ᴅʏɴᴏ ʟᴏɢꜱ.

**⚠️ Read from top**
  ‣ ᴠɪꜱɪᴛ @{SUPPORT_CHAT} ꜰᴏʀ ᴍᴏʀᴇ ɪɴꜰᴏʀᴍᴀᴛɪᴏɴ.
"""

SUDO_HANDLER = CommandHandler(("addsudo", "adddragon"), addsudo)
SUPPORT_HANDLER = CommandHandler(("addsupport", "adddemon"), addsupport)
TIGER_HANDLER = CommandHandler(("addtiger"), addtiger)
WHITELIST_HANDLER = CommandHandler(("addwhitelist", "addwolf"), addwhitelist)
UNSUDO_HANDLER = CommandHandler(("removesudo", "removedragon"), removesudo)
UNSUPPORT_HANDLER = CommandHandler(("removesupport", "removedemon"), removesupport)
UNTIGER_HANDLER = CommandHandler(("removetiger"), removetiger)
UNWHITELIST_HANDLER = CommandHandler(("removewhitelist", "removewolf"), removewhitelist)

WHITELISTLIST_HANDLER = CommandHandler(["whitelistlist", "wolves"], whitelistlist)
TIGERLIST_HANDLER = CommandHandler(["tigers"], tigerlist)
SUPPORTLIST_HANDLER = CommandHandler(["supportlist", "demons"], supportlist)
SUDOLIST_HANDLER = CommandHandler(["sudolist", "dragons"], sudolist)
DEVLIST_HANDLER = CommandHandler(["devlist", "altrons"], devlist)

dispatcher.add_handler(SUDO_HANDLER)
dispatcher.add_handler(SUPPORT_HANDLER)
dispatcher.add_handler(TIGER_HANDLER)
dispatcher.add_handler(WHITELIST_HANDLER)
dispatcher.add_handler(UNSUDO_HANDLER)
dispatcher.add_handler(UNSUPPORT_HANDLER)
dispatcher.add_handler(UNTIGER_HANDLER)
dispatcher.add_handler(UNWHITELIST_HANDLER)

dispatcher.add_handler(WHITELISTLIST_HANDLER)
dispatcher.add_handler(TIGERLIST_HANDLER)
dispatcher.add_handler(SUPPORTLIST_HANDLER)
dispatcher.add_handler(SUDOLIST_HANDLER)
dispatcher.add_handler(DEVLIST_HANDLER)

__mod_name__ = "Dᴇᴠs"
__handlers__ = [
    SUDO_HANDLER,
    SUPPORT_HANDLER,
    TIGER_HANDLER,
    WHITELIST_HANDLER,
    UNSUDO_HANDLER,
    UNSUPPORT_HANDLER,
    UNTIGER_HANDLER,
    UNWHITELIST_HANDLER,
    WHITELISTLIST_HANDLER,
    TIGERLIST_HANDLER,
    SUPPORTLIST_HANDLER,
    SUDOLIST_HANDLER,
    DEVLIST_HANDLER,
]
