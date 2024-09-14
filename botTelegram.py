import logging
import downloadAPI as download
import getMeteringAPI as getMetering
import fileHandler
import json
import readConf as conf
import sendmqtt
from telegram import Update, constants, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

token = "7191232686:AAGls5g11R6VFFwOEy86HaW1gt8bmGDpRbE"
errMessage = "Command nya kurang tepat bre~"

# Load database
# Specify the file name
file_name = 'database.json'

# Loading JSON data
with open(file_name, 'r') as json_file:
    db = json.load(json_file)

# for file in fileHandler.getPath('DAFTAR_IP'):
# garduInduk = file.split("\\")[1].split(".")[0]
# db[garduInduk] = conf.readConf(file)
# Specify the file name

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Define states
CHOOSING_GI, CHOOSING_BAY, CHOOSING_IED = range(3)

# self


def checkMessage(update, context):
    err = [0, 0, 0, 1]

    msg = update.message.text
    msgLen = len(msg.split())

    # Check the command
    if msgLen > 3:
        return err

    elif msgLen < 2:
        return err

    cmd, path, *range = msg.split()

    # Check the path
    if len(path.split("_")) != 3:
        return err

    # Check the range
    if len(range) == 1:
        range = int(range[0])
    else:
        range = 6

    # extract path
    gi, bay, ied = path.split("_")

    # check GI
    if gi not in list(db.keys()):
        return err
    # check bay
    if bay not in list(db[gi].keys()):
        return err

    # check IED
    if ied not in list(db[gi][bay].keys()):
        return err

    iedDatas = db[gi][bay][ied]

    return iedDatas['Ied_IP'], iedDatas["Ied_Brand"], range, 0

# Command Handler


async def liatin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'User : /liatin from {update.message.from_user.first_name}')
    # check data
    addr, brand, range, status = checkMessage(update, context)

    # if err
    if status == 1:
        await update.message.reply_text(errMessage)
        return

    # get list file
    [listFileName, strMsg] = download.getFileList(addr, brand, range)

    # send message
    await update.message.reply_text(strMsg, parse_mode=constants.ParseMode.HTML)
    print("bot : success")


async def ambilin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'User : /ambilin from {update.message.from_user.first_name}')
    # check data
    addr, brand, range, status = checkMessage(update, context)

    # if err
    if status == 1:
        await update.message.reply_text(errMessage)
        return

    # get list file
    [listFileName, strMsg] = download.getFileList(addr, brand, range)

    # check file list
    if listFileName == None:
        await update.message.reply_text(strMsg)
        return

    await update.message.reply_text("tunggu bre~")

    # download the files
    download.getFile(addr, listFileName, brand)

    # open the zip file
    file = open('Records.zip', 'rb')

    # send the file
    await update.message.reply_document(file)
    print("bot : success")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    msg = 'Saya bisa membantu ada untuk melihat dan mengambilkan file pada IED \n\n'
    msg += 'Kamu bisa melakukannya dengan :\n\n'
    msg += '<b>Daftar GI</b>\n'
    msg += '/daftarGI - melihat database GI\n\n'
    msg += '<b>Daftar Bay</b>\n'
    msg += '/daftarBay (GI) - melihat database Bay pada GI\n\n'
    msg += '<b>Daftar IED</b>\n'
    msg += '/daftarIED (GI) (BAY) - melihat database IED pada Bay GI\n\n'
    msg += '<b>LIATIN</b>\n'
    msg += '/liatin - melihat file\n\n'
    msg += '<b>AMBILIN</b>\n'
    msg += '/ambilin - mengambil file\n\n'
    msg += 'Note: Jika kamu tidak mengirimkan jumlahnya, saya akan mengirimkan 6 file terakhir\n\n'
    msg += '<b>METERING</b>\n'
    msg += '/metering - mengambil data metering dari BCU\n\n'

    # send message
    await update.message.reply_text(msg, parse_mode=constants.ParseMode.HTML)


async def daftarGI_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    msg = update.message.text

    msgLen = len(msg.split())
    # Check the command
    if msgLen > 1:
        await update.message.reply_text(errMessage)
        return

    listGI = ', '.join(list(db.keys()))

    await update.message.reply_text(listGI, parse_mode=constants.ParseMode.HTML)
    print("bot : success")


async def metering_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    msg = update.message.text

    msgLen = len(msg.split())
    # Check the command
    if msgLen > 1:
        await update.message.reply_text(errMessage)
        return
    await update.message.reply_text("tunggu bre~")
    meter = getMetering.getMeteringBCU()

    await update.message.reply_text(meter, parse_mode=constants.ParseMode.HTML)
    print("bot : success")


async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text("tunggu bre~")
    client = sendmqtt.connect_mqtt()
    sendmqtt.publish(client, "turun", "tapLink-bksi1/turun")
    client.loop_stop()
    await update.message.reply_text("Sudah Bos!")
    print("bot : success")


async def daftarBay_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    msg = update.message.text
    msgLen = len(msg.split())
    # Check the command
    if msgLen > 2 or msgLen < 2:
        await update.message.reply_text(errMessage)
        return

    cmd, gi = msg.split()

    if gi not in list(db.keys()):
        await update.message.reply_text(errMessage)
        return

    listGI = ', '.join(list(db[gi].keys()))

    await update.message.reply_text(listGI, parse_mode=constants.ParseMode.HTML)
    print("bot : success")


async def daftarIED_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    msg = update.message.text
    msgLen = len(msg.split())
    # Check the command
    if msgLen > 3 or msgLen < 3:
        await update.message.reply_text(errMessage)
        return

    cmd, gi, bay = msg.split()

    if gi not in list(db.keys()):
        await update.message.reply_text(errMessage)
        return

    if bay not in list(db[gi].keys()):
        await update.message.reply_text(errMessage)
        return

    listGI = ', '.join(list(db[gi][bay].keys()))

    await update.message.reply_text(listGI, parse_mode=constants.ParseMode.HTML)
    print("bot : success")

# Starting the conversation


async def start_ambilin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[gi] for gi in db.keys()]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    await update.message.reply_text('Silahkan Pilih GI Bos:', reply_markup=reply_markup)
    return CHOOSING_GI

# Handle GI selection


async def choose_gi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    gi = update.message.text
    if gi in db:
        context.user_data['gi'] = gi
        keyboard = [[bay] for bay in db[gi].keys()]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        await update.message.reply_text('Silahkan Pilih Bay:', reply_markup=reply_markup)
        return CHOOSING_BAY
    else:
        await update.message.reply_text('Salah GI. Ulangi brader.')
        return ConversationHandler.END

# Handle Bay selection


async def choose_bay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bay = update.message.text
    gi = context.user_data['gi']
    if bay in db[gi]:
        context.user_data['bay'] = bay
        keyboard = [[ied] for ied in db[gi][bay].keys()]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        await update.message.reply_text('Silahkan Pilih IED:', reply_markup=reply_markup)
        return CHOOSING_IED
    else:
        await update.message.reply_text('Salah GI. Ulangi brader.')
        return ConversationHandler.END

# Handle IED selection and process request


async def choose_ied(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ied = update.message.text
    gi = context.user_data['gi']
    bay = context.user_data['bay']
    if ied in db[gi][bay]:
        # Process the selected IED
        await update.message.reply_text(f'Konek ke IED: {ied}')

        iedDatas = db[gi][bay][ied]

        # get list file
        [listFileName, strMsg] = download.getFileList(
            iedDatas['Ied_IP'], iedDatas["Ied_Brand"], 6)

        if listFileName == None:
            await update.message.reply_text(strMsg)
            await update.message.reply_text('Tidak ada kodong')
            return ConversationHandler.END

        await update.message.reply_text("tunggu bre~")

        download.getFile(iedDatas['Ied_IP'],
                         listFileName, iedDatas["Ied_Brand"])

        file = open('Records.zip', 'rb')

        await update.message.reply_document(file)

        print("bot : success")

        return ConversationHandler.END
    else:
        await update.message.reply_text('Invalid IED. Please try again.')
        return ConversationHandler.END

# Handle IED selection and process request


async def choose_iedambilin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ied = update.message.text
    gi = context.user_data['gi']
    bay = context.user_data['bay']
    if ied in db[gi][bay]:
        # Process the selected IED
        await update.message.reply_text(f'Konek ke IED: {ied}')

        iedDatas = db[gi][bay][ied]

        # get list file
        [listFileName, strMsg] = download.getFileList(
            iedDatas['Ied_IP'], iedDatas["Ied_Brand"], 6)

        if listFileName == None:
            await update.message.reply_text(strMsg)
            await update.message.reply_text('Tidak ada kodong')
            return ConversationHandler.END

        await update.message.reply_text("tunggu bre~")

        await update.message.reply_text(strMsg, parse_mode=constants.ParseMode.HTML)

        return ConversationHandler.END
    else:
        await update.message.reply_text('Invalid IED. Please try again.')
        return ConversationHandler.END

# Cancel the operation


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Dibatalkan.')
    return ConversationHandler.END


# Error handler
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')

if __name__ == '__main__':
    print("Starting the bot ...")
    application = ApplicationBuilder().token(token).build()

    conv1_handler = ConversationHandler(
        entry_points=[CommandHandler('ambilin', start_ambilin)],
        states={
            CHOOSING_GI: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_gi)],
            CHOOSING_BAY: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_bay)],
            CHOOSING_IED: [MessageHandler(
                filters.TEXT & ~filters.COMMAND, choose_ied)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    conv2_handler = ConversationHandler(
        entry_points=[CommandHandler('liatin', start_ambilin)],
        states={
            CHOOSING_GI: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_gi)],
            CHOOSING_BAY: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_bay)],
            CHOOSING_IED: [MessageHandler(
                filters.TEXT & ~filters.COMMAND, choose_iedambilin)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    # commands
    application.add_handler(conv1_handler)
    application.add_handler(conv2_handler)
    application.add_handler(CommandHandler('liatins', liatin_command))
    application.add_handler(CommandHandler('ambilins', ambilin_command))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('daftarGI', daftarGI_command))
    application.add_handler(CommandHandler('daftarBay', daftarBay_command))
    application.add_handler(CommandHandler('daftarIED', daftarIED_command))
    application.add_handler(CommandHandler('metering', metering_command))
    application.add_handler(CommandHandler('reset', reset_command))

    # errors
    application.add_error_handler(error)

    print("Start Pooling ...")
    application.run_polling()
