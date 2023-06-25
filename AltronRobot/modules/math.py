import math
import pynewtonmath as newton

from telegram import Update
from telegram.ext import CallbackContext, run_async

from AltronRobot import dispatcher
from AltronRobot.modules.disable import DisableAbleCommandHandler


@run_async
def simplify(update: Update, context: CallbackContext):
    args = context.args
    message = update.effective_message
    message.reply_text(newton.simplify("{}".format(args[0])))


@run_async
def factor(update: Update, context: CallbackContext):
    args = context.args
    message = update.effective_message
    message.reply_text(newton.factor("{}".format(args[0])))


@run_async
def derive(update: Update, context: CallbackContext):
    args = context.args
    message = update.effective_message
    message.reply_text(newton.derive("{}".format(args[0])))


@run_async
def integrate(update: Update, context: CallbackContext):
    args = context.args
    message = update.effective_message
    message.reply_text(newton.integrate("{}".format(args[0])))


@run_async
def zeroes(update: Update, context: CallbackContext):
    args = context.args
    message = update.effective_message
    message.reply_text(newton.zeroes("{}".format(args[0])))


@run_async
def tangent(update: Update, context: CallbackContext):
    args = context.args
    message = update.effective_message
    message.reply_text(newton.tangent("{}".format(args[0])))


@run_async
def area(update: Update, context: CallbackContext):
    args = context.args
    message = update.effective_message
    message.reply_text(newton.area("{}".format(args[0])))


@run_async
def cos(update: Update, context: CallbackContext):
    args = context.args
    message = update.effective_message
    message.reply_text(math.cos(int(args[0])))


@run_async
def sin(update: Update, context: CallbackContext):
    args = context.args
    message = update.effective_message
    message.reply_text(math.sin(int(args[0])))


@run_async
def tan(update: Update, context: CallbackContext):
    args = context.args
    message = update.effective_message
    message.reply_text(math.tan(int(args[0])))


@run_async
def arccos(update: Update, context: CallbackContext):
    args = context.args
    message = update.effective_message
    message.reply_text(math.acos(int(args[0])))


@run_async
def arcsin(update: Update, context: CallbackContext):
    args = context.args
    message = update.effective_message
    message.reply_text(math.asin(int(args[0])))


@run_async
def arctan(update: Update, context: CallbackContext):
    args = context.args
    message = update.effective_message
    message.reply_text(math.atan(int(args[0])))


@run_async
def abs(update: Update, context: CallbackContext):
    args = context.args
    message = update.effective_message
    message.reply_text(math.fabs(int(args[0])))


@run_async
def log(update: Update, context: CallbackContext):
    args = context.args
    message = update.effective_message
    message.reply_text(math.log(int(args[0])))


__help__ = """
‣ ꜱᴏʟᴠᴇꜱ ᴄᴏᴍᴘʟᴇx ᴍᴀᴛʜ ᴘʀᴏʙʟᴇᴍꜱ ᴜꜱɪɴɢ https://newton.now.sh

𝗠𝗮𝘁𝗵𝘀:
 ➲ /math : ᴍᴀᴛʜ `/math 2^2+2(2)`
 ➲ /factor : ꜰᴀᴄᴛᴏʀ `/factor x^2 + 2x`
 ➲ /derive : ᴅᴇʀɪᴠᴇ `/derive x^2+2x`
 ➲ /integrate : ɪɴᴛᴇɢʀᴀᴛᴇ `/integrate x^2+2x`
 ➲ /zeroes : ꜰɪɴᴅ 0'ꜱ `/zeroes x^2+2x`
 ➲ /tangent : ꜰɪɴᴅ ᴛᴀɴɢᴇɴᴛ `/tangent 2lx^3`
 ➲ /area : ᴀʀᴇᴀ ᴜɴᴅᴇʀ ᴄᴜʀᴠᴇ `/area 2:4lx^3`
 ➲ /cos : ᴄᴏꜱɪɴᴇ `/cos pi`
 ➲ /sin : ꜱɪɴᴇ `/sin 0`
 ➲ /tan : ᴛᴀɴɢᴇɴᴛ `/tan 0`
 ➲ /arccos : ɪɴᴠᴇʀꜱᴇ ᴄᴏꜱɪɴᴇ `/arccos 1`
 ➲ /arcsin : ɪɴᴠᴇʀꜱᴇ ꜱɪɴᴇ `/arcsin 0`
 ➲ /arctan : ɪɴᴠᴇʀꜱᴇ ᴛᴀɴɢᴇɴᴛ `/arctan 0`
 ➲ /abs : ᴀʙꜱᴏʟᴜᴛᴇ ᴠᴀʟᴜᴇ `/abs -1`
 ➲ /log : ʟᴏɢᴀʀɪᴛʜᴍ `/log 2l8`

*_Keep in Mind_*:
 • ᴛᴏ ꜰɪɴᴅ ᴛʜᴇ ᴛᴀɴɢᴇɴᴛ ʟɪɴᴇ ᴏꜰ ᴀ ꜰᴜɴᴄᴛɪᴏɴ ᴀᴛ ᴀ ᴄᴇʀᴛᴀɪɴ x ᴠᴀʟᴜᴇ, ꜱᴇɴᴅ ᴛʜᴇ ʀᴇQᴜᴇꜱᴛ ᴀꜱ c|f(x) ᴡʜᴇʀᴇ c ɪꜱ ᴛʜᴇ ɢɪᴠᴇɴ x ᴠᴀʟᴜᴇ ᴀɴᴅ f(x) ɪꜱ ᴛʜᴇ ꜰᴜɴᴄᴛɪᴏɴ ᴇxᴘʀᴇꜱꜱɪᴏɴ, ᴛʜᴇ ꜱᴇᴘᴀʀᴀᴛᴏʀ ɪꜱ ᴀ ᴠᴇʀᴛɪᴄᴀʟ ʙᴀʀ '|'. ꜱᴇᴇ ᴛʜᴇ ᴛᴀʙʟᴇ ᴀʙᴏᴠᴇ ꜰᴏʀ ᴀɴ ᴇxᴀᴍᴘʟᴇ ʀᴇQᴜᴇꜱᴛ.

 • ᴛᴏ ꜰɪɴᴅ ᴛʜᴇ ᴀʀᴇᴀ ᴜɴᴅᴇʀ ᴀ ꜰᴜɴᴄᴛɪᴏɴ, ꜱᴇɴᴅ ᴛʜᴇ ʀᴇQᴜᴇꜱᴛ ᴀꜱ c:d|f(x) ᴡʜᴇʀᴇ c ɪꜱ ᴛʜᴇ ꜱᴛᴀʀᴛɪɴɢ x ᴠᴀʟᴜᴇ, d ɪꜱ ᴛʜᴇ ᴇɴᴅɪɴɢ x ᴠᴀʟᴜᴇ, ᴀɴᴅ f(x) ɪꜱ ᴛʜᴇ ꜰᴜɴᴄᴛɪᴏɴ ᴜɴᴅᴇʀ ᴡʜɪᴄʜ ʏᴏᴜ ᴡᴀɴᴛ ᴛʜᴇ ᴄᴜʀᴠᴇ ʙᴇᴛᴡᴇᴇɴ ᴛʜᴇ ᴛᴡᴏ x ᴠᴀʟᴜᴇꜱ.

‣ ᴛᴏ ᴄᴏᴍᴘᴜᴛᴇ ꜰʀᴀᴄᴛɪᴏɴꜱ, ᴇɴᴛᴇʀ ᴇxᴘʀᴇꜱꜱɪᴏɴꜱ ᴀꜱ ɴᴜᴍᴇʀᴀᴛᴏʀ(over)ᴅᴇɴᴏᴍɪɴᴀᴛᴏʀ.
  *ꜰᴏʀ ᴇxᴀᴍᴘʟᴇ:* ᴛᴏ ᴘʀᴏᴄᴇꜱꜱ 2/4 ʏᴏᴜ ᴍᴜꜱᴛ ꜱᴇɴᴅ ɪɴ ʏᴏᴜʀ ᴇxᴘʀᴇꜱꜱɪᴏɴ ᴀꜱ 2(over)4. ᴛʜᴇ ʀᴇꜱᴜʟᴛ ᴇxᴘʀᴇꜱꜱɪᴏɴ ᴡɪʟʟ ʙᴇ ɪɴ ꜱᴛᴀɴᴅᴀʀᴅ ᴍᴀᴛʜ ɴᴏᴛᴀᴛɪᴏɴ (1/2, 3/4).
"""

__mod_name__ = "Mᴀᴛʜs"


SIMPLIFY_HANDLER = DisableAbleCommandHandler("math", simplify)
FACTOR_HANDLER = DisableAbleCommandHandler("factor", factor)
DERIVE_HANDLER = DisableAbleCommandHandler("derive", derive)
INTEGRATE_HANDLER = DisableAbleCommandHandler("integrate", integrate)
ZEROES_HANDLER = DisableAbleCommandHandler("zeroes", zeroes)
TANGENT_HANDLER = DisableAbleCommandHandler("tangent", tangent)
AREA_HANDLER = DisableAbleCommandHandler("area", area)
COS_HANDLER = DisableAbleCommandHandler("cos", cos)
SIN_HANDLER = DisableAbleCommandHandler("sin", sin)
TAN_HANDLER = DisableAbleCommandHandler("tan", tan)
ARCCOS_HANDLER = DisableAbleCommandHandler("arccos", arccos)
ARCSIN_HANDLER = DisableAbleCommandHandler("arcsin", arcsin)
ARCTAN_HANDLER = DisableAbleCommandHandler("arctan", arctan)
ABS_HANDLER = DisableAbleCommandHandler("abs", abs)
LOG_HANDLER = DisableAbleCommandHandler("log", log)

dispatcher.add_handler(SIMPLIFY_HANDLER)
dispatcher.add_handler(FACTOR_HANDLER)
dispatcher.add_handler(DERIVE_HANDLER)
dispatcher.add_handler(INTEGRATE_HANDLER)
dispatcher.add_handler(ZEROES_HANDLER)
dispatcher.add_handler(TANGENT_HANDLER)
dispatcher.add_handler(AREA_HANDLER)
dispatcher.add_handler(COS_HANDLER)
dispatcher.add_handler(SIN_HANDLER)
dispatcher.add_handler(TAN_HANDLER)
dispatcher.add_handler(ARCCOS_HANDLER)
dispatcher.add_handler(ARCSIN_HANDLER)
dispatcher.add_handler(ARCTAN_HANDLER)
dispatcher.add_handler(ABS_HANDLER)
dispatcher.add_handler(LOG_HANDLER)
