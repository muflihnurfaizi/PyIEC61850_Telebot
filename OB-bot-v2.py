import os
import logging
import json
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, constants
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler, CallbackQueryHandler
from functools import wraps


# Load environment variables from the .env file
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


# Define states
CHOOSING_BAY, CHOOSING_IED, CHOOSING_ACTION = range(3)
ERR_MESSAGE = "Command nya kurang tepat bre~"


# Load database
# Specify the file name
file_name = 'database.json'


# logger
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# Loading JSON data
try:
    with open(file_name, 'r') as json_file:
        db = json.load(json_file)
except (FileNotFoundError, json.JSONDecodeError) as e:
    print(f"Error loading database: {e}")
    db = {}


# Custom middleware to check if bot is tagged in group chats
def check_mention(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        if update.message:
            # If the message is from a group or supergroup
            if update.message.chat.type in ['group', 'supergroup']:
                # Check if the bot is mentioned in the message
                if f"@{context.bot.username}" in update.message.text:
                    return await func(update, context, *args, **kwargs)
                else:
                    # Do nothing if the bot is not tagged
                    return
            else:
                # If it's a private chat, respond directly
                return await func(update, context, *args, **kwargs)
        else:
            # For callback queries, just proceed
            return await func(update, context, *args, **kwargs)
    return wrapper


# Commands
@check_mention
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    msg = (
        "Saya bisa membantu ada untuk melihat dan mengambilkan file pada IED\n\n"
        "Kamu bisa melakukannya dengan:\n\n"
        "<b>FILES</b>\n"
        "/files - melihat atau mendownload file pada IED\n"
        "Saya akan mengirimkan 6 file terakhir pada IED\n\n"
        "<b>METERING</b>\n"
        "/metering - mengambil data metering dari BCU\n\n"
    )
    # send message
    await update.message.reply_text(msg, parse_mode=constants.ParseMode.HTML)


@check_mention
async def statuscb_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Ini start command')


@check_mention
async def metering_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        await update.message.reply_text(ERR_MESSAGE)
        return
    await update.message.reply_text("tunggu bre~")
    print("bot : success")


# Start conversation
@check_mention
async def start_conv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Create inline keyboard dynamically from db.keys()
    keyboard = [[InlineKeyboardButton(bays, callback_data=bays)]
                for bays in db.keys()]

    # Create the inline keyboard markup
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send a message with the inline keyboard
    await update.message.reply_text('Silahkan Pilih GI Bos:', reply_markup=reply_markup)

    # Set the state to CHOOSING_BAY
    return CHOOSING_BAY


# Handle GI selection
async def choose_bay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # Acknowledge the callback

    bay = query.data  # Get the selected bay from callback data
    if bay in db:
        # Store the selected bay in user_data
        context.user_data['bay'] = bay

        # Create an inline keyboard from db[bay].keys()
        keyboard = [[InlineKeyboardButton(
            bay_option, callback_data=bay_option)] for bay_option in db[bay].keys()]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Send a message with the inline keyboard
        await query.edit_message_text('Silahkan Pilih IED:', reply_markup=reply_markup)

        return CHOOSING_IED
    else:
        # Handle the case where the bay is invalid
        await query.edit_message_text('Salah Bay. Ulangi brader.')
        return ConversationHandler.END


# Handle IED selection and process request
async def choose_ied(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    ied = query.data  # Get the selected IED from callback data
    bay = context.user_data['bay']
    if ied in db[bay]:
        context.user_data['ied'] = ied

        # Provide actions for the user to choose
        keyboard = [
            [InlineKeyboardButton("Liatin", callback_data='liatin')],
            [InlineKeyboardButton("Ambilin", callback_data='ambilin')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(f'Pilihanmu: {ied}. Terus, mau apa brader?:', reply_markup=reply_markup)
        return CHOOSING_ACTION

    else:
        await query.edit_message_text('Salah IED. Ulangi brader.')
        return ConversationHandler.END


async def choose_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    action = query.data  # Either 'liatin' or 'ambilin'
    bay = context.user_data['bay']
    ied = context.user_data['ied']
    iedDatas = db[bay][ied]

    if action == 'liatin':
        await query.edit_message_text(f"Menampilkan data untuk Bay: {bay}, IED: {ied}. Data: {iedDatas}")
    elif action == 'ambilin':
        await query.edit_message_text(f"Mengambil data untuk Bay: {bay}, IED: {ied}. Data: {iedDatas}")

    return ConversationHandler.END


# Cancel the operation
@check_mention
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Dibatalkan.')
    return ConversationHandler.END


# Error handler
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')


# Run the app
if __name__ == '__main__':
    print("Starting the bot ...")

    application = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('files', start_conv)],
        states={
            CHOOSING_BAY: [CallbackQueryHandler(choose_bay)],
            CHOOSING_IED: [CallbackQueryHandler(choose_ied)],
            CHOOSING_ACTION: [CallbackQueryHandler(choose_action)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    # Add handlers to the application
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('metering', metering_command))
    application.add_handler(CommandHandler('statuscb', statuscb_command))

    # Add error handler
    application.add_error_handler(error)

    print("Start Polling ...")
    application.run_polling()
