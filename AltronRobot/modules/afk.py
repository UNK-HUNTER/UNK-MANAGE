import html

from telegram import MessageEntity, Update
from telegram.error import BadRequest
from telegram.ext import CallbackContext, Filters, MessageHandler, run_async

from AltronRobot import dispatcher
from AltronRobot.modules.disable import (
    DisableAbleCommandHandler,
    DisableAbleMessageHandler,
)
from AltronRobot.modules.sql import afk_sql as sql
from AltronRobot.modules.users import get_user_id

AFK_GROUP = 7
AFK_REPLY_GROUP = 8


@run_async
def afk(update: Update, context: CallbackContext):
    args = update.effective_message.text.split(None, 1)
    user = update.effective_user

    if not user:  # ignore channels
        return

    if user.id in [777000, 1087968824]:
        return

    if len(args) >= 2:
        reason = args[1]
        if len(reason) > 131:
            reason = reason[:131]
    else:
        reason = ""

    sql.set_afk(update.effective_user.id, reason)
    fname = update.effective_user.first_name
    try:
        update.effective_message.reply_text(f"{fname} ɪꜱ ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ")
    except BadRequest:
        pass


@run_async
def no_longer_afk(update: Update, context: CallbackContext):
    user = update.effective_user
    message = update.effective_message

    if not user:  # ignore channels
        return

    res = sql.rm_afk(user.id)
    if res:
        if message.new_chat_members:  # dont say msg
            return
        firstname = update.effective_user.first_name
        try:
            update.effective_message.reply_text(f"{firstname} ɪꜱ ʙᴀᴄᴋ ᴏɴʟɪɴᴇ")
        except:
            return


@run_async
def reply_afk(update: Update, context: CallbackContext):
    bot = context.bot
    message = update.effective_message
    userc = update.effective_user
    userc_id = userc.id
    if message.entities and message.parse_entities(
        [MessageEntity.TEXT_MENTION, MessageEntity.MENTION]
    ):
        entities = message.parse_entities(
            [MessageEntity.TEXT_MENTION, MessageEntity.MENTION]
        )

        chk_users = []
        for ent in entities:
            if ent.type == MessageEntity.TEXT_MENTION:
                user_id = ent.user.id
                fst_name = ent.user.first_name

                if user_id in chk_users:
                    return
                chk_users.append(user_id)

            if ent.type != MessageEntity.MENTION:
                return

            user_id = get_user_id(message.text[ent.offset : ent.offset + ent.length])
            if not user_id:
                # Should never happen, since for a user to become AFK they must have spoken. Maybe changed username?
                return

            if user_id in chk_users:
                return
            chk_users.append(user_id)

            try:
                chat = bot.get_chat(user_id)
            except BadRequest:
                print(f"ᴇʀʀᴏʀ: ᴄᴏᴜʟᴅ ɴᴏᴛ ꜰᴇᴛᴄʜ ᴜꜱᴇʀɪᴅ {user_id} ꜰᴏʀ ᴀꜰᴋ ᴍᴏᴅᴜʟᴇ")
                return
            fst_name = chat.first_name

            check_afk(update, context, user_id, fst_name, userc_id)

    elif message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        fst_name = message.reply_to_message.from_user.first_name
        check_afk(update, context, user_id, fst_name, userc_id)


def check_afk(update, context, user_id, fst_name, userc_id):
    if sql.is_afk(user_id):
        user = sql.check_afk_status(user_id)
        if int(userc_id) == int(user_id):
            return
        if not user.reason:
            res = f"{fst_name} ɪꜱ ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ"
            update.effective_message.reply_text(res)
        else:
            res = "{} ɪꜱ ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ.\n\n» ʀᴇᴀꜱᴏɴ: <code>{}</code>".format(
                html.escape(fst_name), html.escape(user.reason)
            )
            update.effective_message.reply_text(res, parse_mode="html")


__help__ = """
𝗔𝘄𝗮𝘆 𝗳𝗿𝗼𝗺 𝗴𝗿𝗼𝘂𝗽:
  ➲ /afk <reason>: ᴍᴀʀᴋ ʏᴏᴜʀꜱᴇʟꜰ ᴀꜱ ᴀꜰᴋ(ᴀᴡᴀʏ ꜰʀᴏᴍ ᴋᴇʏʙᴏᴀʀᴅ).
  ➲ brb <reason>: ꜱᴀᴍᴇ ᴀꜱ ᴛʜᴇ ᴀꜰᴋ ᴄᴏᴍᴍᴀɴᴅ - ʙᴜᴛ ɴᴏᴛ ᴀ ᴄᴏᴍᴍᴀɴᴅ.

 ‣ ᴡʜᴇɴ ᴍᴀʀᴋᴇᴅ ᴀꜱ ᴀꜰᴋ, ᴀɴʏ ᴍᴇɴᴛɪᴏɴꜱ ᴡɪʟʟ ʙᴇ ʀᴇᴘʟɪᴇᴅ ᴛᴏ ᴡɪᴛʜ ᴀ ᴍᴇꜱꜱᴀɢᴇ ᴛᴏ ꜱᴀʏ ʏᴏᴜ'ʀᴇ ɴᴏᴛ ᴀᴠᴀɪʟᴀʙʟᴇ!
"""

AFK_HANDLER = DisableAbleCommandHandler("afk", afk)
AFK_REGEX_HANDLER = DisableAbleMessageHandler(
    Filters.regex(r"^(?i)brb(.*)$"), afk, friendly="afk"
)
NO_AFK_HANDLER = MessageHandler(Filters.all & Filters.group, no_longer_afk)
AFK_REPLY_HANDLER = MessageHandler(Filters.all & Filters.group, reply_afk)

dispatcher.add_handler(AFK_HANDLER, AFK_GROUP)
dispatcher.add_handler(AFK_REGEX_HANDLER, AFK_GROUP)
dispatcher.add_handler(NO_AFK_HANDLER, AFK_GROUP)
dispatcher.add_handler(AFK_REPLY_HANDLER, AFK_REPLY_GROUP)

__mod_name__ = "Aꜰᴋ​"
__command_list__ = ["afk"]
__handlers__ = [
    (AFK_HANDLER, AFK_GROUP),
    (AFK_REGEX_HANDLER, AFK_GROUP),
    (NO_AFK_HANDLER, AFK_GROUP),
    (AFK_REPLY_HANDLER, AFK_REPLY_GROUP),
]
