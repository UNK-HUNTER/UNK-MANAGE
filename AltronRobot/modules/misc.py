import requests
import wikipedia

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Update
from telegram.ext import CallbackContext, CommandHandler, Filters
from telegram.ext.dispatcher import run_async
from wikipedia.exceptions import DisambiguationError, PageError

from AltronRobot import dispatcher
from AltronRobot.modules.disable import DisableAbleCommandHandler
from AltronRobot.modules.helper_funcs.chat_status import user_admin


MARKDOWN_HELP = f"""
‣ ᴍᴀʀᴋᴅᴏᴡɴ ɪꜱ ᴀ ᴠᴇʀʏ ᴘᴏᴡᴇʀꜰᴜʟ ꜰᴏʀᴍᴀᴛᴛɪɴɢ ᴛᴏᴏʟ ꜱᴜᴘᴘᴏʀᴛᴇᴅ ʙʏ ᴛᴇʟᴇɢʀᴀᴍ.

‣ {dispatcher.bot.first_name} ʜᴀꜱ ꜱᴏᴍᴇ ᴇɴʜᴀɴᴄᴇᴍᴇɴᴛꜱ, ᴛᴏ ᴍᴀᴋᴇ ꜱᴜʀᴇ ᴛʜᴀᴛ ꜱᴀᴠᴇᴅ ᴍᴇꜱꜱᴀɢᴇꜱ ᴀʀᴇ ᴄᴏʀʀᴇᴄᴛʟʏ ᴘᴀʀꜱᴇᴅ, ᴀɴᴅ ᴛᴏ ᴀʟʟᴏᴡ ʏᴏᴜ ᴛᴏ ᴄʀᴇᴀᴛᴇ ʙᴜᴛᴛᴏɴꜱ.

• <code>_italic_</code>: ᴡʀᴀᴘᴘɪɴɢ ᴛᴇxᴛ ᴡɪᴛʜ '_' ᴡɪʟʟ ᴘʀᴏᴅᴜᴄᴇ ɪᴛᴀʟɪᴄ ᴛᴇxᴛ
• <code>*bold*</code>: ᴡʀᴀᴘᴘɪɴɢ ᴛᴇxᴛ ᴡɪᴛʜ '*' ᴡɪʟʟ ᴘʀᴏᴅᴜᴄᴇ ʙᴏʟᴅ ᴛᴇxᴛ
• <code>`code`</code>: ᴡʀᴀᴘᴘɪɴɢ ᴛᴇxᴛ ᴡɪᴛʜ '`' ᴡɪʟʟ ᴘʀᴏᴅᴜᴄᴇ ᴍᴏɴᴏꜱᴘᴀᴄᴇᴅ ᴛᴇxᴛ, ᴀʟꜱᴏ ᴋɴᴏᴡɴ ᴀꜱ 'ᴄᴏᴅᴇ'

• <code>[SomeText](SomeURL)</code>: ᴛʜɪꜱ ᴡɪʟʟ ᴄʀᴇᴀᴛᴇ ᴀ ʟɪɴᴋ - ᴛʜᴇ ᴍᴇꜱꜱᴀɢᴇ ᴡɪʟʟ ᴊᴜꜱᴛ ꜱʜᴏᴡ <code>SomeText</code>.
  <b>Example:</b><code>[Altron](https://t.me/TheAltron)</code>

• <code>[ButtonText](buttonurl:SomeURL)</code>: ᴛʜɪꜱ ɪꜱ ᴀ ꜱᴘᴇᴄɪᴀʟ ᴇɴʜᴀɴᴄᴇᴍᴇɴᴛ ᴛᴏ ᴀʟʟᴏᴡ ᴜꜱᴇʀꜱ ᴛᴏ ʜᴀᴠᴇ ᴛᴇʟᴇɢʀᴀᴍ ʙᴜᴛᴛᴏɴꜱ ɪɴ ᴛʜᴇɪʀ ᴍᴀʀᴋᴅᴏᴡɴ. <code>ButtonText</code> ᴡɪʟʟ ʙᴇ ᴡʜᴀᴛ ɪꜱ ᴅɪꜱᴘʟᴀʏᴇᴅ ᴏɴ ᴛʜᴇ ʙᴜᴛᴛᴏɴ, ᴀɴᴅ <code>SomeURL</code> ᴡɪʟʟ ʙᴇ ᴛʜᴇ ᴜʀʟ ᴡʜɪᴄʜ ɪꜱ ᴏᴘᴇɴᴇᴅ.
  <b>Example:</b> <code>[This is a button](buttonurl:https://t.me/TheAltron)</code>

‣ ɪꜰ ʏᴏᴜ ᴡᴀɴᴛ ᴍᴜʟᴛɪᴘʟᴇ ʙᴜᴛᴛᴏɴꜱ ᴏɴ ᴛʜᴇ ꜱᴀᴍᴇ ʟɪɴᴇ, ᴜꜱᴇ <code>:same</code>, ᴀꜱ ꜱᴜᴄʜ:
  <code>[one](buttonurl://example.com)
  [two](buttonurl://google.com:same)</code>
 • ᴛʜɪꜱ ᴡɪʟʟ ᴄʀᴇᴀᴛᴇ ᴛᴡᴏ ʙᴜᴛᴛᴏɴꜱ ᴏɴ ᴀ ꜱɪɴɢʟᴇ ʟɪɴᴇ, ɪɴꜱᴛᴇᴀᴅ ᴏꜰ ᴏɴᴇ ʙᴜᴛᴛᴏɴ ᴘᴇʀ ʟɪɴᴇ.

‣ ᴋᴇᴇᴘ ɪɴ ᴍɪɴᴅ ᴛʜᴀᴛ ʏᴏᴜʀ ᴍᴇꜱꜱᴀɢᴇ <b>ᴍᴜꜱᴛ</b> ᴄᴏɴᴛᴀɪɴ ꜱᴏᴍᴇ ᴛᴇxᴛ ᴏᴛʜᴇʀ ᴛʜᴀɴ ᴊᴜꜱᴛ ᴀ ʙᴜᴛᴛᴏɴ!
"""


@run_async
@user_admin
def echo(update: Update, context: CallbackContext):
    args = update.effective_message.text.split(None, 1)
    message = update.effective_message

    if message.reply_to_message:
        message.reply_to_message.reply_text(
            args[1], parse_mode="MARKDOWN", disable_web_page_preview=True
        )
    else:
        message.reply_text(
            args[1], quote=False, parse_mode="MARKDOWN", disable_web_page_preview=True
        )
    message.delete()


def markdown_help_sender(update: Update):
    update.effective_message.reply_text(MARKDOWN_HELP, parse_mode=ParseMode.HTML)
    update.effective_message.reply_text(
        "Try forwarding the following message to me, and you'll see, and Use #test!"
    )
    update.effective_message.reply_text(
        "/save test This is a markdown test. _italics_, *bold*, code, "
        "[URL](example.com) [button](buttonurl:github.com) "
        "[button2](buttonurl://google.com:same)"
    )


@run_async
def markdown_help(update: Update, context: CallbackContext):
    if update.effective_chat.type != "private":
        update.effective_message.reply_text(
            "» ᴄᴏɴᴛᴀᴄᴛ ᴍᴇ ɪɴ ᴘᴍ",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "• ᴍᴀʀᴋᴅᴏᴡɴ ʜᴇʟᴘ •",
                            url=f"t.me/{context.bot.username}?start=markdownhelp",
                        )
                    ]
                ]
            ),
        )
        return
    markdown_help_sender(update)


@run_async
def ud(update: Update, context: CallbackContext):
    message = update.effective_message
    text = message.text.split(" ", 1)[1]
    results = requests.get(f"https://api.urbandictionary.com/v0/define?term={text}").json()
    try:
        reply_text = f'» *{text}*\n\n‣ {results["list"][0]["definition"]}\n\n‣ _{results["list"][0]["example"]}_'
    except:
        reply_text = "» ɴᴏ ʀᴇꜱᴜʟᴛꜱ ꜰᴏᴜɴᴅ."
    message.reply_text(reply_text, parse_mode=ParseMode.MARKDOWN)


@run_async
def wiki(update: Update, context: CallbackContext):
    msg = (
        update.effective_message.reply_to_message
        if update.effective_message.reply_to_message
        else update.effective_message
    )
    res = ""
    if msg == update.effective_message:
        search = msg.text.split(" ", maxsplit=1)[1]
    else:
        search = msg.text
    try:
        res = wikipedia.summary(search)
    except DisambiguationError as e:
        update.message.reply_text(
            "Disambiguated pages found! Adjust your query accordingly.\n<i>{}</i>".format(
                e
            ),
            parse_mode=ParseMode.HTML,
        )
    except PageError as e:
        update.message.reply_text(
            "<code>{}</code>".format(e), parse_mode=ParseMode.HTML
        )
    if res:
        result = f"<b>{search}</b>\n\n"
        result += f"<i>{res}</i>\n"
        result += f"""<a href="https://en.wikipedia.org/wiki/{search.replace(" ", "%20")}">Read more...</a>"""
        if len(result) > 4000:
            with open("result.txt", "w") as f:
                f.write(f"{result}\n\n ~ @TheAltron")
            with open("result.txt", "rb") as f:
                context.bot.send_document(
                    document=f,
                    filename=f.name,
                    reply_to_message_id=update.message.message_id,
                    chat_id=update.effective_chat.id,
                    parse_mode=ParseMode.HTML,
                )
        else:
            update.message.reply_text(
                result, parse_mode=ParseMode.HTML, disable_web_page_preview=True
            )


__help__ = """
*Markdown:*
  ➲ /markdownhelp: Qᴜɪᴄᴋ ꜱᴜᴍᴍᴀʀʏ ᴏꜰ ʜᴏᴡ ᴍᴀʀᴋᴅᴏᴡɴ ᴡᴏʀᴋꜱ ɪɴ ᴛᴇʟᴇɢʀᴀᴍ - ᴄᴀɴ ᴏɴʟʏ ʙᴇ ᴄᴀʟʟᴇᴅ ɪɴ ᴘʀɪᴠᴀᴛᴇ ᴄʜᴀᴛꜱ

*React:*
  ➲ /react: ʀᴇᴀᴄᴛꜱ ᴡɪᴛʜ ᴀ ʀᴀɴᴅᴏᴍ ʀᴇᴀᴄᴛɪᴏɴ

*Urban Dictonary:*
  ➲ /ud <ᴛᴇxᴛ>: ꜱᴇᴀʀᴄʜꜱ ᴛʜᴇ ɢɪᴠᴇɴ ᴛᴇxᴛ ᴏɴ ᴜʀʙᴀɴ ᴅɪᴄᴛɪᴏɴᴀʀʏ ᴀɴᴅ ꜱᴇɴᴅꜱ ʏᴏᴜ ᴛʜᴇ ɪɴꜰᴏʀᴍᴀᴛɪᴏɴ.

*Wikipedia:*
  ➲ /wiki <text> : ꜱᴇᴀʀᴄʜꜱ ᴀʙᴏᴜᴛ ᴛʜᴇ ɢɪᴠᴇɴ ᴛᴇxᴛ ᴏɴ ᴡɪᴋɪᴘᴇᴅɪᴀ.

*Wallpapers:*
  ➲ /wall <query>: ɢᴇᴛ ᴀ ᴡᴀʟʟᴘᴀᴘᴇʀ ꜰʀᴏᴍ wall.alphacoders.com

*Currency converter:* 
  ➲ /cash: ᴄᴜʀʀᴇɴᴄʏ ᴄᴏɴᴠᴇʀᴛᴇʀ
Example:
 `/cash 1 USD INR`  
      _OR_
 `/cash 1 usd inr`
ᴏᴜᴛᴘᴜᴛ: `1.0 USD = 75.505 INR`
"""

ECHO_HANDLER = DisableAbleCommandHandler("echo", echo, filters=Filters.group)
MD_HELP_HANDLER = CommandHandler("markdownhelp", markdown_help)
UD_HANDLER = DisableAbleCommandHandler(["ud"], ud)
WIKI_HANDLER = DisableAbleCommandHandler("wiki", wiki)

dispatcher.add_handler(ECHO_HANDLER)
dispatcher.add_handler(MD_HELP_HANDLER)
dispatcher.add_handler(UD_HANDLER)
dispatcher.add_handler(WIKI_HANDLER)

__mod_name__ = "Exᴛʀᴀs"
__command_list__ = ["id", "echo", "ud", "wiki"]
__handlers__ = [
    ECHO_HANDLER,
    MD_HELP_HANDLER,
    UD_HANDLER,
    WIKI_HANDLER
]
