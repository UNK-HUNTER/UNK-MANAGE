from telegram import Update
from telegram.ext import CallbackContext

from AltronRobot import dispatcher
from AltronRobot.modules.disable import DisableAbleCommandHandler

from TruthDarePy import TD

love = TD()


def truth(update: Update, context: CallbackContext):
    update.effective_message.reply_text(love.truth(lang="en"))

def dare(update: Update, context: CallbackContext):
    update.effective_message.reply_text(love.dare(lang="en"))


TRUTH_HANDLER = DisableAbleCommandHandler("truth", truth)
DARE_HANDLER = DisableAbleCommandHandler("dare", dare)

dispatcher.add_handler(TRUTH_HANDLER)
dispatcher.add_handler(DARE_HANDLER)


__help__ = """
𝗧𝗿𝘂𝘁𝗵 & 𝗗𝗮𝗿𝗲:
  ➲ /truth : ꜱᴇɴᴅꜱ ᴀ ʀᴀɴᴅᴏᴍ ᴛʀᴜᴛʜ ꜱᴛʀɪɴɢ.
  ➲ /dare : ꜱᴇɴᴅꜱ ᴀ ʀᴀɴᴅᴏᴍ ᴅᴀʀᴇ ꜱᴛʀɪɴɢ.
"""

__mod_name__ = "Tʀᴜᴛʜ-Dᴀʀᴇ"
