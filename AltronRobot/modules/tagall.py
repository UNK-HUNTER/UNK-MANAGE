import asyncio

from telethon import events
from telethon.errors import UserNotParticipantError
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.tl.types import ChannelParticipantAdmin, ChannelParticipantCreator

from AltronRobot import telethn

spam_chats = []


@telethn.on(events.NewMessage(pattern="^/tagall ?(.*)"))
@telethn.on(events.NewMessage(pattern="^@all ?(.*)"))
async def mentionall(event):
    chat_id = event.chat_id
    if event.is_private:
        return await event.respond("» ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ᴄᴀɴ ʙᴇ ᴜꜱᴇ ɪɴ ɢʀᴏᴜᴘꜱ ᴀɴᴅ ᴄʜᴀɴɴᴇʟꜱ!")

    is_admin = False
    try:
        partici_ = await telethn(GetParticipantRequest(event.chat_id, event.sender_id))
    except UserNotParticipantError:
        is_admin = False
    else:
        if isinstance(
            partici_.participant, (ChannelParticipantAdmin, ChannelParticipantCreator)
        ):
            is_admin = True
    if not is_admin:
        return await event.respond("» ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴍᴇɴᴛɪᴏɴ ᴀʟʟ!")

    if event.pattern_match.group(1) and event.is_reply:
        return await event.respond("» ɢɪᴠᴇ ᴍᴇ ᴏɴᴇ ᴀʀɢᴜᴍᴇɴᴛ!")
    elif event.is_reply:
        mode = "text_on_reply"
        msg = await event.get_reply_message()
        if msg == None:
            return await event.respond(
                "» ɪ ᴄᴀɴ'ᴛ ᴍᴇɴᴛɪᴏɴ ᴍᴇᴍʙᴇʀꜱ ꜰᴏʀ ᴏʟᴅᴇʀ ᴍᴇꜱꜱᴀɢᴇꜱ! (ᴍᴇꜱꜱᴀɢᴇꜱ ᴡʜɪᴄʜ ᴀʀᴇ ꜱᴇɴᴛ ʙᴇꜰᴏʀᴇ ɪ'ᴍ ᴀᴅᴅᴇᴅ ᴛᴏ ɢʀᴏᴜᴘ)"
            )
    elif event.pattern_match.group(1):
        mode = "text_on_cmd"
        msg = event.pattern_match.group(1)
    else:
        return await event.respond(
            "» ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇꜱꜱᴀɢᴇ ᴏʀ ɢɪᴠᴇ ᴍᴇ ꜱᴏᴍᴇ ᴛᴇxᴛ ᴛᴏ ᴍᴇɴᴛɪᴏɴ ᴏᴛʜᴇʀꜱ!"
        )

    spam_chats.append(chat_id)
    usrnum = 0
    usrtxt = ""
    async for usr in telethn.iter_participants(chat_id):
        if not chat_id in spam_chats:
            break
        usrnum += 1
        usrtxt += f"[{usr.first_name}](tg://user?id={usr.id}), "
        if usrnum == 5:
            if mode == "text_on_cmd":
                txt = f"{msg}\n{usrtxt}"
                await telethn.send_message(chat_id, txt)
            elif mode == "text_on_reply":
                await msg.reply(usrtxt)
            await asyncio.sleep(1)
            usrnum = 0
            usrtxt = ""
    try:
        spam_chats.remove(chat_id)
    except:
        pass


@telethn.on(events.NewMessage(pattern="^/cancel$"))
async def cancel_spam(event):
    if not event.chat_id in spam_chats:
        return await event.respond("» ᴛʜᴇʀᴇ ɪꜱ ɴᴏ ᴘʀᴏᴄᴄᴇꜱꜱ ᴏɴ ɢᴏɪɴɢ...")
    is_admin = False
    try:
        partici_ = await telethn(GetParticipantRequest(event.chat_id, event.sender_id))
    except UserNotParticipantError:
        is_admin = False
    else:
        if isinstance(
            partici_.participant, (ChannelParticipantAdmin, ChannelParticipantCreator)
        ):
            is_admin = True
    if not is_admin:
        return await event.respond("» ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴇxᴇᴄᴜᴛᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ!")

    else:
        try:
            spam_chats.remove(event.chat_id)
        except:
            pass
        return await event.respond("» ꜱᴛᴏᴘᴘᴇᴅ ᴍᴇɴᴛɪᴏɴ.")


__mod_name__ = "Tᴀɢ Aʟʟ​"
__help__ = """
──「 Only for Admins 」──

 ➲ /tagall ᴏʀ @all (ʀᴇᴘʟʏ ᴛᴏ ᴍᴇꜱꜱᴀɢᴇ ᴏʀ ᴀᴅᴅ ᴀɴᴏᴛʜᴇʀ ᴍᴇꜱꜱᴀɢᴇ): ᴛᴏ ᴍᴇɴᴛɪᴏɴ ᴀʟʟ ᴍᴇᴍʙᴇʀꜱ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ, ᴡɪᴛʜᴏᴜᴛ ᴇxᴄᴇᴘᴛɪᴏɴ.
 ➲ /cancel : ꜰᴏʀ ᴄᴀɴᴄᴇʟɪɴɢ ᴛʜᴇ ᴍᴇɴᴛɪᴏɴ-ᴀʟʟ.
"""
