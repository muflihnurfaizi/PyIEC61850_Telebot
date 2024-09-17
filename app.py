# This file is part of OB-bot.
# OB-bot is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import os
import logging
import json
import random
import datetime
import locale
from api import bcu_api
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, constants
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler, CallbackQueryHandler
from functools import wraps
from apscheduler.schedulers.asyncio import AsyncIOScheduler


# Set locale ke bahasa Indonesia
locale.setlocale(locale.LC_TIME, 'id_ID.UTF-8')

# Define states
CHOOSING_BAY, CHOOSING_IED, CHOOSING_ACTION = range(3)
ERR_MESSAGE = "Command nya kurang tepat bre~"


# Load database
# Specify the file name
databaseIED = 'databaseIED.json'
databaseBCU = 'databaseBCU.json'
config_file = 'config.json'


# File to store subscribers
SUBSCRIPTION_FILE = 'subscribers.json'


# Local API function
def local_api_check():
    """Simulate a local API by returning a random boolean."""
    return random.choice([True, False])  # Simulates your local Python function


# Function to load and save subscribers
def load_subscribers():
    """Load subscribers from a JSON file."""
    if os.path.exists(SUBSCRIPTION_FILE):
        with open(SUBSCRIPTION_FILE, 'r') as file:
            return json.load(file)
    return []


def save_subscribers(subscribers):
    """Save subscribers to a JSON file."""
    with open(SUBSCRIPTION_FILE, 'w') as file:
        json.dump(subscribers, file)


# Load the subscribers initially
subscribers = load_subscribers()


# Check Routine
async def check_local_api_and_notify(context: ContextTypes.DEFAULT_TYPE):
    """This function checks the local API and sends notifications to subscribers if needed."""
    try:
        api_result = local_api_check()  # Call your local API function
        if api_result:
            message = "Local API returned True! Here's your notification."
            # Notify all subscribers
            for user_id in subscribers:
                await context.bot.send_message(chat_id=user_id, text=message)
    except Exception as e:
        print(f"Error while checking the local API: {e}")

# logger
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# Loading database IED
try:
    with open(databaseIED, 'r') as json_file:
        db_IED = json.load(json_file)
except (FileNotFoundError, json.JSONDecodeError) as e:
    print(f"Error loading database: {e}")
    db_IED = {}

# Loading database BCU
try:
    with open(databaseBCU, 'r') as json_file:
        db_BCU = json.load(json_file)
except (FileNotFoundError, json.JSONDecodeError) as e:
    print(f"Error loading database: {e}")
    db_BCU = {}

# Loading config file
try:
    with open(config_file, 'r') as json_file:
        config = json.load(json_file)
except (FileNotFoundError, json.JSONDecodeError) as e:
    print(f"Error loading database: {e}")
    config = {}


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
    metering = bcu_api.getMeteringBCU(db_BCU, type=config.get("TYPE_BCU"))

    results_str = ""
    results_str += f"DATA METERING {config.get("SUBSTATION_NAME")}\n"
    # Dapatkan waktu sekarang
    now = datetime.datetime.now()
    # Format string sesuai kebutuhan
    results_str += now.strftime("Tanggal : %d %B %Y, Pukul %H:%M WIB")

    for bay_name, measurements in metering.items():
        # Extract and format the required values
        curr_phs_b = str(round(measurements.get('currPhsB', 0.0)))
        volt_phs_ca = str(round(measurements.get('voltPhsCA', 0.0)))
        w = str(round(measurements.get('W', 0.0)))
        var = str(round(measurements.get('VAR', 0.0)))

        # Print the extracted and formatted information for each bay
        results_str += f"{bay_name}: {curr_phs_b} A, {volt_phs_ca} kV, {w} MW, {var} Mvar \n"

    print(results_str)
    print("bot : success")


@check_mention
async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Subscribe the user to the local API notifications."""
    user_id = update.message.chat_id

    if user_id not in subscribers:
        subscribers.append(user_id)
        save_subscribers(subscribers)  # Persist the new subscriber
        await update.message.reply_text("Oke brader. Nanti saya infokan kalau ada kejadian.")
    else:
        await update.message.reply_text("Sudah terdaftar brader.")


@check_mention
async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Unsubscribe the user from the local API notifications."""
    user_id = update.message.chat_id

    if user_id in subscribers:
        subscribers.remove(user_id)
        save_subscribers(subscribers)  # Persist the updated subscriber list
        await update.message.reply_text("Elaahh, kenapa si.")
    else:
        await update.message.reply_text("Belum terdaftar brader.")


# Start conversation
@check_mention
async def start_conv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Create inline keyboard dynamically from db.keys()
    keyboard = [[InlineKeyboardButton(bays, callback_data=bays)]
                for bays in db_IED.keys()]

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
    if bay in db_IED:
        # Store the selected bay in user_data
        context.user_data['bay'] = bay

        # Create an inline keyboard from db[bay].keys()
        keyboard = [[InlineKeyboardButton(
            bay_option, callback_data=bay_option)] for bay_option in db_IED[bay].keys()]
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
    if ied in db_IED[bay]:
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
    iedDatas = db_IED[bay][ied]

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

    # Initialize bot and scheduler
    application = ApplicationBuilder().token(
        config.get('TELEGRAM_BOT_TOKEN')).build()
    scheduler = AsyncIOScheduler()

    # Conversation Handler
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
    application.add_handler(CommandHandler('infoindong', subscribe))
    application.add_handler(CommandHandler('stopinfoin', unsubscribe))

    # Schedule the local API check every minute
    scheduler.add_job(check_local_api_and_notify, 'interval',
                      seconds=60, args=[application])

    # Add error handler
    application.add_error_handler(error)

    # Start scheduler and polling
    scheduler.start()
    print("Start Polling ...")
    application.run_polling()
