from telegram.ext import *
from telegram import *
from telegram.error import *
import logging
from owoify.owoify import owoify, Owoness
from html import escape
from uuid import uuid4

from os import getenv

__import__("dotenv").load_dotenv()


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

logging.getLogger("httpx").setLevel(logging.WARNING)


TOKEN = getenv("TOKEN")

def get_owoness(owoness: str) -> Owoness | None:
    match owoness:
        case "owo":
            return Owoness.Owo
        case "uwu":
            return Owoness.Uwu
        case "uvu":
            return Owoness.Uvu
        case _:
            return None

def owo(message: Message, level: str):
    text = message.text or message.caption
    owo_text = owoify(text, get_owoness(level))
    return owo_text


def get_settings_text(current_setting: str):
    text = (
        "Choose a level between these three:\n\n" 

        "• owo : The most vanilla one\n" 
        "• uwu (default): The moderate one\n" 
        "• uvu: Literally unreadable\n\n" 
        
        f"Current level: <b>{current_setting}</b>\n\n" 
            
        "Example:\n" 
        f"<i>{escape(owoify('The quick brown fox jumps over the lazy dog.', get_owoness(current_setting)))}</i>"
    )


    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(f"{'✅' if current_setting == 'owo' else ''} owo", callback_data='owo'),
                InlineKeyboardButton(f"{'✅' if current_setting == 'uwu' else ''} uwu", callback_data='uwu'),
                InlineKeyboardButton(f"{'✅' if current_setting == 'uvu' else ''} uvu", callback_data='uvu')
            ]
        ]
    )
    return text, keyboard



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text=(
            "Welcwomwe two this bwot! (*^ω^)\n"
            "With this bwot u'ww be able two owoify any text mwessage that u want! "
            "U can send any mwessage in chat, or use mwe in gwoups repwying two other mwessages with /owo ヽ(*・ω・)ﾉ\n"
            "U can alswo change teh levwl of owonyess with /settings!\n"
            "<i>(if you want a readable version of this message, use /better_start...)</i>\n\n"
                    
            "<b>Made by @KyryUnTizioh (*^.^*)</b>"
        ),
        parse_mode='HTML'
    )

async def better_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text=(
            "Welcome to this bot!\n"
            "With this bot you'll be able to owoify any text message that you want! "
            "You can send any message in chat, or use me in groups replying to other messages with /owo!\n"
            "You can also change the level of owoness with /settings!\n\n"

            "<b>Made by @KyryUnTizioh (*^.^*)</b>"
        ),
        parse_mode='HTML')


async def owo_private(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = owo(update.effective_message, context.chat_data.get('owo_level', 'uwu'))
    await update.effective_message.reply_text(text[:1024])

async def owo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_message.reply_to_message:
        text = owo(update.effective_message.reply_to_message, context.chat_data.get('owo_level', 'uwu'))
        await update.effective_message.reply_to_message.reply_text(text[:1024])
    else:
        await update.effective_message.reply_text('Use fwis cwommand two owoify othew mwessages!! (*￣з￣)')

async def owo_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    current_setting = context.chat_data.get('owo_level', 'uwu')

    text, keyboard = get_settings_text(current_setting)

    await update.effective_message.reply_text(
        text=text,
        parse_mode='HTML',
        reply_markup=keyboard
    )

async def inline_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if update.effective_chat.type in ('group', 'supergroup') and update.effective_user.id not in (admin.user.id for admin in await context.bot.get_chat_administrators(update.effective_chat.id)):
        await query.answer('fwis cwommand is fwow admins onwy!!! ÒwÓ', show_alert=True)
        return
    current_setting = context.chat_data.get('owo_level', 'uwu')
    if query.data == current_setting:
        await query.answer()
    else:
        current_setting = context.chat_data['owo_level'] = query.data
        text, keyboard = get_settings_text(current_setting)
        await query.edit_message_text(
            text=text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        await query.answer('dwonye!!!')

async def inline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query
    results = []
    if query:
        results = [
            InlineQueryResultArticle(
                id=uuid4(), title="Level: owo", input_message_content=InputTextMessageContent(owoify(query, Owoness.Owo))
            ),
            InlineQueryResultArticle(
                id=uuid4(), title="Level: uwu", input_message_content=InputTextMessageContent(owoify(query, Owoness.Uwu))
            ),
            InlineQueryResultArticle(
                id=uuid4(), title="Level: uvu", input_message_content=InputTextMessageContent(owoify(query, Owoness.Uvu))
            ),
        ]
    await update.inline_query.answer(results, button=InlineQueryResultsButton("Help", start_parameter="inline"))


def main():

    application = (
        Application
        .builder()
        .token(TOKEN)
        .persistence(PicklePersistence("persistence.pickle"))
        .concurrent_updates(True)
        .build()
    )
    

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('better_start', better_start))
    application.add_handler(CommandHandler(['owoify', 'owo', 'uwuify', 'uwu'], owo_command))
    application.add_handler(CommandHandler('settings', owo_settings))
    application.add_handler(MessageHandler(filters.ChatType.PRIVATE & (filters.TEXT | filters.CAPTION), owo_private))
    application.add_handler(CallbackQueryHandler(inline_settings))
    application.add_handler(InlineQueryHandler(inline))


    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
