import html

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Update
from telegram.error import BadRequest
from telegram.ext import CallbackContext, CallbackQueryHandler, run_async
from telegram.utils.helpers import mention_html

import AltronRobot.modules.sql.approve_sql as sql
from AltronRobot import DRAGONS, dispatcher
from AltronRobot.modules.disable import DisableAbleCommandHandler
from AltronRobot.modules.helper_funcs.chat_status import user_admin
from AltronRobot.modules.helper_funcs.extraction import extract_user
from AltronRobot.modules.channel import loggable


@loggable
@user_admin
@run_async
def approve(update, context):
    message = update.effective_message
    chat_title = message.chat.title
    chat = update.effective_chat
    args = context.args
    user = update.effective_user
    user_id = extract_user(message, args)
    if not user_id:
        message.reply_text(
            "» ɪ ᴅᴏɴ'ᴛ ᴋɴᴏᴡ ᴡʜᴏ ʏᴏᴜ'ʀᴇ ᴛᴀʟᴋɪɴɢ ᴀʙᴏᴜᴛ, ʏᴏᴜ'ʀᴇ ɢᴏɪɴɢ ᴛᴏ ɴᴇᴇᴅ ᴛᴏ ꜱᴘᴇᴄɪꜰʏ ᴀ ᴜꜱᴇʀ!"
        )
        return ""
    try:
        member = chat.get_member(user_id)
    except BadRequest:
        return ""
    if member.status == "administrator" or member.status == "creator":
        message.reply_text(
            "» ᴜꜱᴇʀ ɪꜱ ᴀʟʀᴇᴀᴅʏ ᴀᴅᴍɪɴ - ʟᴏᴄᴋꜱ, ʙʟᴏᴄᴋʟɪꜱᴛꜱ, ᴀɴᴅ ᴀɴᴛɪꜰʟᴏᴏᴅ ᴀʟʀᴇᴀᴅʏ ᴅᴏɴ'ᴛ ᴀᴘᴘʟʏ ᴛᴏ ᴛʜᴇᴍ."
        )
        return ""
    if sql.is_approved(message.chat_id, user_id):
        message.reply_text(
            f"» [{member.user['first_name']}](tg://user?id={member.user['id']}) ɪꜱ ᴀʟʀᴇᴀᴅʏ ᴀᴘᴘʀᴏᴠᴇᴅ ɪɴ {chat_title}",
            parse_mode=ParseMode.MARKDOWN,
        )
        return ""
    sql.approve(message.chat_id, user_id)
    message.reply_text(
        f"» [{member.user['first_name']}](tg://user?id={member.user['id']}) ʜᴀꜱ ʙᴇᴇɴ ᴀᴘᴘʀᴏᴠᴇᴅ ɪɴ {chat_title}!\n» ᴛʜᴇʏ ᴡɪʟʟ ɴᴏᴡ ʙᴇ ɪɢɴᴏʀᴇᴅ ʙʏ ᴀᴜᴛᴏᴍᴀᴛᴇᴅ ᴀᴅᴍɪɴ ᴀᴄᴛɪᴏɴꜱ ʟɪᴋᴇ ʟᴏᴄᴋꜱ, ʙʟᴏᴄᴋʟɪꜱᴛꜱ, ᴀɴᴅ ᴀɴᴛɪꜰʟᴏᴏᴅ.",
        parse_mode=ParseMode.MARKDOWN,
    )
    return ""


@loggable
@user_admin
@run_async
def disapprove(update, context):
    message = update.effective_message
    chat_title = message.chat.title
    chat = update.effective_chat
    args = context.args
    user = update.effective_user
    user_id = extract_user(message, args)
    if not user_id:
        message.reply_text(
            "» ɪ ᴅᴏɴ'ᴛ ᴋɴᴏᴡ ᴡʜᴏ ʏᴏᴜ'ʀᴇ ᴛᴀʟᴋɪɴɢ ᴀʙᴏᴜᴛ, ʏᴏᴜ'ʀᴇ ɢᴏɪɴɢ ᴛᴏ ɴᴇᴇᴅ ᴛᴏ ꜱᴘᴇᴄɪꜰʏ ᴀ ᴜꜱᴇʀ!"
        )
        return ""
    try:
        member = chat.get_member(user_id)
    except BadRequest:
        return ""
    if member.status == "administrator" or member.status == "creator":
        message.reply_text("» ᴛʜɪꜱ ᴜꜱᴇʀ ɪꜱ ᴀɴ ᴀᴅᴍɪɴ, ᴛʜᴇʏ ᴄᴀɴ'ᴛ ʙᴇ ᴜɴᴀᴘᴘʀᴏᴠᴇᴅ.")
        return ""
    if not sql.is_approved(message.chat_id, user_id):
        message.reply_text(f"» {member.user['first_name']} ɪꜱɴ'ᴛ ᴀᴘᴘʀᴏᴠᴇᴅ ʏᴇᴛ!")
        return ""
    sql.disapprove(message.chat_id, user_id)
    message.reply_text(f"» {member.user['first_name']} ɪꜱ ɴᴏ ʟᴏɴɢᴇʀ ᴀᴘᴘʀᴏᴠᴇᴅ ɪɴ {chat_title}.")
    return ""


@user_admin
@run_async
def approved(update, context):
    message = update.effective_message
    chat_title = message.chat.title
    chat = update.effective_chat
    msg = "» ᴛʜᴇ ꜰᴏʟʟᴏᴡɪɴɢ ᴜꜱᴇʀꜱ ᴀʀᴇ ᴀᴘᴘʀᴏᴠᴇᴅ.\n"
    approved_users = sql.list_approved(message.chat_id)
    for i in approved_users:
        member = chat.get_member(int(i.user_id))
        msg += f"- `{i.user_id}`: {member.user['first_name']}\n"
    if msg.endswith("ᴀᴘᴘʀᴏᴠᴇᴅ.\n"):
        message.reply_text(f"» ɴᴏ ᴜꜱᴇʀꜱ ᴀʀᴇ ᴀᴘᴘʀᴏᴠᴇᴅ ɪɴ {chat_title}.")
        return ""
    else:
        message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)


@user_admin
@run_async
def approval(update, context):
    message = update.effective_message
    chat = update.effective_chat
    args = context.args
    user_id = extract_user(message, args)
    member = chat.get_member(int(user_id))
    if not user_id:
        message.reply_text("» ɪ ᴅᴏɴ'ᴛ ᴋɴᴏᴡ ᴡʜᴏ ʏᴏᴜ'ʀᴇ ᴛᴀʟᴋɪɴɢ ᴀʙᴏᴜᴛ, ʏᴏᴜ'ʀᴇ ɢᴏɪɴɢ ᴛᴏ ɴᴇᴇᴅ ᴛᴏ ꜱᴘᴇᴄɪꜰʏ ᴀ ᴜꜱᴇʀ!")
        return ""
    if sql.is_approved(message.chat_id, user_id):
        message.reply_text(
            f"» {member.user['first_name']} ɪꜱ ᴀɴ ᴀᴘᴘʀᴏᴠᴇᴅ ᴜꜱᴇʀ.\n» ʟᴏᴄᴋꜱ, ᴀɴᴛɪꜰʟᴏᴏᴅ, ᴀɴᴅ ʙʟᴏᴄᴋʟɪꜱᴛꜱ ᴡᴏɴ'ᴛ ᴀᴘᴘʟʏ ᴛᴏ ᴛʜᴇᴍ."
        )
    else:
        message.reply_text(
            f"» {member.user['first_name']} ɪꜱ ɴᴏᴛ ᴀɴ ᴀᴘᴘʀᴏᴠᴇᴅ ᴜꜱᴇʀ.\n» ᴛʜᴇʏ ᴀʀᴇ ᴀꜰꜰᴇᴄᴛᴇᴅ ʙʏ ɴᴏʀᴍᴀʟ ᴄᴏᴍᴍᴀɴᴅꜱ."
        )


@run_async
def unapproveall(update: Update, context: CallbackContext):
    chat = update.effective_chat
    user = update.effective_user
    member = chat.get_member(user.id)
    if member.status != "creator" and user.id not in DRAGONS:
        update.effective_message.reply_text(
            "» ᴏɴʟʏ ᴛʜᴇ ᴄʜᴀᴛ ᴏᴡɴᴇʀ ᴄᴀɴ ᴜɴᴀᴘᴘʀᴏᴠᴇ ᴀʟʟ ᴜꜱᴇʀꜱ ᴀᴛ ᴏɴᴄᴇ."
        )
    else:
        buttons = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="ᴜɴᴀᴘᴘʀᴏᴠᴇ ᴀʟʟ", callback_data="unapproveall_user"
                    ),
                    InlineKeyboardButton(
                        text="ᴄᴀɴᴄᴇʟ", callback_data="unapproveall_cancel"
                    )
                ],
            ]
        )
        update.effective_message.reply_text(
            f"» ᴀʀᴇ ʏᴏᴜ ꜱᴜʀᴇ ʏᴏᴜ ᴡᴏᴜʟᴅ ʟɪᴋᴇ ᴛᴏ ᴜɴᴀᴘᴘʀᴏᴠᴇ ᴀʟʟ ᴜꜱᴇʀꜱ ɪɴ {chat.title}?\n» ᴛʜɪꜱ ᴀᴄᴛɪᴏɴ ᴄᴀɴɴᴏᴛ ʙᴇ ᴜɴᴅᴏɴᴇ.",
            reply_markup=buttons,
            parse_mode=ParseMode.MARKDOWN,
        )


@run_async
def unapproveall_btn(update: Update, context: CallbackContext):
    query = update.callback_query
    chat = update.effective_chat
    message = update.effective_message
    member = chat.get_member(query.from_user.id)
    if query.data == "unapproveall_user":
        if member.status == "creator" or query.from_user.id in DRAGONS:
            approved_users = sql.list_approved(chat.id)
            users = [int(i.user_id) for i in approved_users]
            for user_id in users:
                sql.disapprove(chat.id, user_id)
            message.edit_text("» ᴜɴᴀᴘᴘʀᴏᴠᴇᴅ ᴀʟʟ ᴜꜱᴇʀꜱ.")

        if member.status == "administrator":
            query.answer("Only owner of the chat can do this.")

        if member.status == "member":
            query.answer("You need to be admin to do this.")
    elif query.data == "unapproveall_cancel":
        if member.status == "creator" or query.from_user.id in DRAGONS:
            message.edit_text("» ʀᴇᴍᴏᴠɪɴɢ ᴏꜰ ᴀʟʟ ᴀᴘᴘʀᴏᴠᴇᴅ ᴜꜱᴇʀꜱ ʜᴀꜱ ʙᴇᴇɴ ᴄᴀɴᴄᴇʟʟᴇᴅ.")
            return ""
        if member.status == "administrator":
            query.answer("Only owner of the chat can do this.")
        if member.status == "member":
            query.answer("You need to be admin to do this.")


__help__ = """
‣ Sometimes, you might trust a user not to send unwanted content.
‣ Maybe not enough to make them admin, but you might be ok with locks, blacklists, and antiflood not applying to them.

‣ ᴛʜᴀᴛ'ꜱ ᴡʜᴀᴛ ᴀᴘᴘʀᴏᴠᴀʟꜱ ᴀʀᴇ ꜰᴏʀ - ᴀᴘᴘʀᴏᴠᴇ ᴏꜰ ᴛʀᴜꜱᴛᴡᴏʀᴛʜʏ ᴜꜱᴇʀꜱ ᴛᴏ ᴀʟʟᴏᴡ ᴛʜᴇᴍ ᴛᴏ ꜱᴇɴᴅ

𝗔𝗱𝗺𝗶𝗻 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀:
  ➲ /approval: ᴄʜᴇᴄᴋ ᴀ ᴜꜱᴇʀ'ꜱ ᴀᴘᴘʀᴏᴠᴀʟ ꜱᴛᴀᴛᴜꜱ ɪɴ ᴛʜɪꜱ ᴄʜᴀᴛ.
  ➲ /approve: ᴀᴘᴘʀᴏᴠᴇ ᴏꜰ ᴀ ᴜꜱᴇʀ. ʟᴏᴄᴋꜱ, ʙʟᴀᴄᴋʟɪꜱᴛꜱ, ᴀɴᴅ ᴀɴᴛɪꜰʟᴏᴏᴅ ᴡᴏɴ'ᴛ ᴀᴘᴘʟʏ ᴛᴏ ᴛʜᴇᴍ ᴀɴʏᴍᴏʀᴇ.
  ➲ /unapprove: ᴜɴᴀᴘᴘʀᴏᴠᴇ ᴏꜰ ᴀ ᴜꜱᴇʀ. ᴛʜᴇʏ ᴡɪʟʟ ɴᴏᴡ ʙᴇ ꜱᴜʙᴊᴇᴄᴛ ᴛᴏ ʟᴏᴄᴋꜱ, ʙʟᴀᴄᴋʟɪꜱᴛꜱ, ᴀɴᴅ ᴀɴᴛɪꜰʟᴏᴏᴅ ᴀɢᴀɪɴ.
  ➲ /approved: ʟɪꜱᴛ ᴀʟʟ ᴀᴘᴘʀᴏᴠᴇᴅ ᴜꜱᴇʀꜱ.
  ➲ /unapproveall: ᴜɴᴀᴘᴘʀᴏᴠᴇ ᴀʟʟ ᴜꜱᴇʀꜱ ɪɴ ᴀ ᴄʜᴀᴛ. ᴛʜɪꜱ ᴄᴀɴɴᴏᴛ ʙᴇ ᴜɴᴅᴏɴᴇ.
"""

APPROVE = DisableAbleCommandHandler("approve", approve)
DISAPPROVE = DisableAbleCommandHandler("unapprove", disapprove)
APPROVED = DisableAbleCommandHandler("approved", approved)
APPROVAL = DisableAbleCommandHandler("approval", approval)
UNAPPROVEALL = DisableAbleCommandHandler("unapproveall", unapproveall)
UNAPPROVEALL_BTN = CallbackQueryHandler(unapproveall_btn, pattern=r"unapproveall_.*")

dispatcher.add_handler(APPROVE)
dispatcher.add_handler(DISAPPROVE)
dispatcher.add_handler(APPROVED)
dispatcher.add_handler(APPROVAL)
dispatcher.add_handler(UNAPPROVEALL)
dispatcher.add_handler(UNAPPROVEALL_BTN)

__mod_name__ = "Aᴘᴘʀᴏᴠᴇ"
__command_list__ = ["approve", "unapprove", "approved", "approval"]
__handlers__ = [APPROVE, DISAPPROVE, APPROVED, APPROVAL]
