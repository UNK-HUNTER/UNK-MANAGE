from datetime import datetime
from functools import wraps

from telegram.ext import CallbackContext

from AltronRobot.modules.helper_funcs.misc import is_module_loaded

FILENAME = __name__.rsplit(".", 1)[-1]

if is_module_loaded(FILENAME):
    from telegram import ParseMode, Update
    from telegram.error import BadRequest, Unauthorized
    from telegram.ext import CommandHandler, JobQueue, run_async
    from telegram.utils.helpers import escape_markdown

    from AltronRobot import EVENT_LOGS, LOGGER, dispatcher
    from AltronRobot.modules.helper_funcs.chat_status import user_admin
    from AltronRobot.modules.sql import log_channel_sql as sql

    def loggable(func):
        @wraps(func)
        def log_action(
            update: Update,
            context: CallbackContext,
            job_queue: JobQueue = None,
            *args,
            **kwargs,
        ):
            if not job_queue:
                result = func(update, context, *args, **kwargs)
            else:
                result = func(update, context, job_queue, *args, **kwargs)

            chat = update.effective_chat
            message = update.effective_message

            if result:
                datetime_fmt = "%H:%M - %d-%m-%Y"
                result += f"\n» <b>ᴇᴠᴇɴᴛ sᴛᴀᴍᴘ</b>: <code>{datetime.utcnow().strftime(datetime_fmt)}</code>"

                if message.chat.type == chat.SUPERGROUP and message.chat.username:
                    result += f'\n» <b>ʟɪɴᴋ:</b> <a href="https://t.me/{chat.username}/{message.message_id}">ᴄʟɪᴄᴋ ʜᴇʀᴇ</a>'
                log_chat = sql.get_chat_log_channel(chat.id)
                if log_chat:
                    send_log(context, log_chat, chat.id, result)

            return result

        return log_action

    def gloggable(func):
        @wraps(func)
        def glog_action(update: Update, context: CallbackContext, *args, **kwargs):
            result = func(update, context, *args, **kwargs)
            chat = update.effective_chat
            message = update.effective_message

            if result:
                datetime_fmt = "%H:%M - %d-%m-%Y"
                result += "\n» <b>ᴇᴠᴇɴᴛ sᴛᴀᴍᴘ</b>: <code>{}</code>".format(
                    datetime.utcnow().strftime(datetime_fmt)
                )

                if message.chat.type == chat.SUPERGROUP and message.chat.username:
                    result += f'\n» <b>ʟɪɴᴋ:</b> <a href="https://t.me/{chat.username}/{message.message_id}">ᴄʟɪᴄᴋ ʜᴇʀᴇ</a>'
                log_chat = str(EVENT_LOGS)
                if log_chat:
                    send_log(context, log_chat, chat.id, result)

            return result

        return glog_action

    def send_log(
        context: CallbackContext, log_chat_id: str, orig_chat_id: str, result: str
    ):
        bot = context.bot
        try:
            bot.send_message(
                log_chat_id,
                result,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
            )
        except BadRequest as excp:
            if excp.message == "Chat not found":
                bot.send_message(orig_chat_id, "» ᴛʜɪs ʟᴏɢ ᴄʜᴀɴɴᴇʟ ʜᴀs ʙᴇᴇɴ ᴅᴇʟᴇᴛᴇᴅ - ᴜɴsᴇᴛᴛɪɴɢ.")
                sql.stop_chat_logging(orig_chat_id)
            else:
                LOGGER.warning(excp.message)
                LOGGER.warning(result)
                LOGGER.exception("Could not parse")

                bot.send_message(
                    log_chat_id,
                    result
                    + "\n\n» ғᴏʀᴍᴀᴛᴛɪɴɢ ʜᴀs ʙᴇᴇɴ ᴅɪsᴀʙʟᴇᴅ ᴅᴜᴇ ᴛᴏ ᴀɴ ᴜɴᴇxᴘᴇᴄᴛᴇᴅ ᴇʀʀᴏʀ.",
                )

    @run_async
    @user_admin
    def logging(update: Update, context: CallbackContext):
        bot = context.bot
        message = update.effective_message
        chat = update.effective_chat

        log_channel = sql.get_chat_log_channel(chat.id)
        if log_channel:
            log_channel_info = bot.get_chat(log_channel)
            message.reply_text(
                f"» ᴛʜɪs ɢʀᴏᴜᴘ ʜᴀs ᴀʟʟ ɪᴛ's ʟᴏɢs sᴇɴᴛ ᴛᴏ:"
                f" {escape_markdown(log_channel_info.title)} (`{log_channel}`)",
                parse_mode=ParseMode.MARKDOWN,
            )
        else:
            message.reply_text("» ɴᴏ ʟᴏɢ ᴄʜᴀɴɴᴇʟ ʜᴀs ʙᴇᴇɴ sᴇᴛ ғᴏʀ ᴛʜɪs ɢʀᴏᴜᴘ!")

    @run_async
    @user_admin
    def setlog(update: Update, context: CallbackContext):
        bot = context.bot
        message = update.effective_message
        chat = update.effective_chat
        if chat.type == chat.CHANNEL:
            message.reply_text("» ɴᴏᴡ, ꜰᴏʀᴡᴀʀᴅ ᴛʜᴇ /setlog ᴛᴏ ᴛʜᴇ ɢʀᴏᴜᴘ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴛɪᴇ ᴛʜɪꜱ ᴄʜᴀɴɴᴇʟ ᴛᴏ!")

        elif message.forward_from_chat:
            sql.set_chat_log_channel(chat.id, message.forward_from_chat.id)
            try:
                message.delete()
            except BadRequest as excp:
                if excp.message == "Message to delete not found":
                    pass
                else:
                    LOGGER.exception("Error deleting message in log channel. Should work anyway though.")

            try:
                bot.send_message(
                    message.forward_from_chat.id,
                    f"» ᴛʜɪꜱ ᴄʜᴀɴɴᴇʟ ʜᴀꜱ ʙᴇᴇɴ ꜱᴇᴛ ᴀꜱ ᴛʜᴇ ʟᴏɢ ᴄʜᴀɴɴᴇʟ ꜰᴏʀ {chat.title or chat.first_name}.",
                )
            except Unauthorized as excp:
                if excp.message == "Forbidden: bot is not a member of the channel chat":
                    bot.send_message(chat.id, "» ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ꜱᴇᴛ ʟᴏɢ ᴄʜᴀɴɴᴇʟ!")
                else:
                    LOGGER.exception("ERROR in setting the log channel.")

            bot.send_message(chat.id, "» ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ꜱᴇᴛ ʟᴏɢ ᴄʜᴀɴɴᴇʟ!")

        else:
            message.reply_text(
                "» ᴛʜᴇ ꜱᴛᴇᴘꜱ ᴛᴏ ꜱᴇᴛ ᴀ ʟᴏɢ ᴄʜᴀɴɴᴇʟ ᴀʀᴇ:\n"
                " - ᴀᴅᴅ ʙᴏᴛ ᴛᴏ ᴛʜᴇ ᴅᴇꜱɪʀᴇᴅ ᴄʜᴀɴɴᴇʟ\n"
                " - ꜱᴇɴᴅ /setlog ᴛᴏ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ\n"
                " - ꜰᴏʀᴡᴀʀᴅ ᴛʜᴇ /setlog ᴛᴏ ᴛʜᴇ ɢʀᴏᴜᴘ\n"
            )

    @run_async
    @user_admin
    def unsetlog(update: Update, context: CallbackContext):
        bot = context.bot
        message = update.effective_message
        chat = update.effective_chat

        log_channel = sql.stop_chat_logging(chat.id)
        if log_channel:
            bot.send_message(
                log_channel, f"» ᴄʜᴀɴɴᴇʟ ʜᴀꜱ ʙᴇᴇɴ ᴜɴʟɪɴᴋᴇᴅ ꜰʀᴏᴍ {chat.title}"
            )
            message.reply_text("» ʟᴏɢ ᴄʜᴀɴɴᴇʟ ʜᴀꜱ ʙᴇᴇɴ ᴜɴ-ꜱᴇᴛ.")

        else:
            message.reply_text("» ɴᴏ ʟᴏɢ ᴄʜᴀɴɴᴇʟ ʜᴀꜱ ʙᴇᴇɴ ꜱᴇᴛ ʏᴇᴛ!")

    def __stats__():
        return f"• {sql.num_logchannels()} ʟᴏɢ ᴄʜᴀɴɴᴇʟꜱ ꜱᴇᴛ."

    def __migrate__(old_chat_id, new_chat_id):
        sql.migrate_chat(old_chat_id, new_chat_id)

    def __chat_settings__(chat_id, user_id):
        log_channel = sql.get_chat_log_channel(chat_id)
        if log_channel:
            log_channel_info = dispatcher.bot.get_chat(log_channel)
            return f"» ᴛʜɪꜱ ɢʀᴏᴜᴘ ʜᴀꜱ ᴀʟʟ ɪᴛ'ꜱ ʟᴏɢꜱ ꜱᴇɴᴛ ᴛᴏ: {escape_markdown(log_channel_info.title)} (`{log_channel}`)"
        return "» ɴᴏ ʟᴏɢ ᴄʜᴀɴɴᴇʟ ɪꜱ ꜱᴇᴛ ꜰᴏʀ ᴛʜɪꜱ ɢʀᴏᴜᴘ!"

    __help__ = """
𝗔𝗱𝗺𝗶𝗻𝘀 𝗼𝗻𝗹𝘆:
 ➲ /logchannel : ɢᴇᴛ ʟᴏɢ ᴄʜᴀɴɴᴇʟ ɪɴғᴏ
 ➲ /setlog : sᴇᴛ ᴛʜᴇ ʟᴏɢ ᴄʜᴀɴɴᴇʟ
 ➲ /unsetlog : ᴜɴsᴇᴛ ᴛʜᴇ ʟᴏɢ ᴄʜᴀɴɴᴇʟ

𝗦𝗲𝘁𝘁𝗶𝗻𝗴 𝘁𝗵𝗲 𝗹𝗼𝗴 𝗰𝗵𝗮𝗻𝗻𝗲𝗹 𝗶𝘀 𝗱𝗼𝗻𝗲 𝗯𝘆:
 1. ᴀᴅᴅɪɴɢ ᴛʜᴇ ʙᴏᴛ ᴛᴏ ᴛʜᴇ ᴅᴇsɪʀᴇᴅ ᴄʜᴀɴɴᴇʟ (ᴀs ᴀɴ ᴀᴅᴍɪɴ!)
 2. sᴇɴᴅɪɴɢ /setlog ɪɴ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ
 3. ғᴏʀᴡᴀʀᴅɪɴɢ ᴛʜᴇ /setlog ᴛᴏ ᴛʜᴇ ɢʀᴏᴜᴘ
"""

    __mod_name__ = "Cʜᴀɴɴᴇʟ"

    LOG_HANDLER = CommandHandler("logchannel", logging)
    SET_LOG_HANDLER = CommandHandler("setlog", setlog)
    UNSET_LOG_HANDLER = CommandHandler("unsetlog", unsetlog)

    dispatcher.add_handler(LOG_HANDLER)
    dispatcher.add_handler(SET_LOG_HANDLER)
    dispatcher.add_handler(UNSET_LOG_HANDLER)

else:
    # run anyway if module not loaded
    def loggable(func):
        return func

    def gloggable(func):
        return func
