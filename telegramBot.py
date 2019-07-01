
"""
First, a few callback functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import logging

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)

token = "669087829:AAGKDCOfyOwmAKMLlOvhyK9ziEM_pIJzqDs"

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

MODE = range(4)


def start(update, context):
    reply_keyboard = [['Criar Ordem'], ['Editar Ordem'], ['Ver Ordens']]

    update.message.reply_text(
        'Olá, meu nome é Dom Setup, estou aqui para auxiliar em seus investimentos.'
        'Envie /cancelar para parar de falar de falar comigo.\n\n'
        'O que deseja fazer?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return MODE


def set_mode(update, context):
    user = update.message.from_user
    mode = update.message.text.lower()
    answer = "Certo, deseja " + mode + "\nSó um segundo, " + user.first_name
    logger.info("Modo escolhido por %s: %s", user.first_name, update.message.text)
    update.message.reply_text(answer, reply_markup=ReplyKeyboardRemove())

    if mode == 'criar ordem':
        update.message.reply_text('Opção 1: Em desenvolvimento....', reply_markup=ReplyKeyboardRemove())
    if mode == 'editar ordens':
        update.message.reply_text('Opção 2: Em desenvolvimento....', reply_markup=ReplyKeyboardRemove())
    if mode == 'ver ordens':
        see_orders_mode(update, context)


def see_orders_mode(update, context):
    my_sheet = google_sheets_connector()
    orders = get_orders_from_sheet(my_sheet)
    for each_order in orders:
        update.message.reply_text(each_order, reply_markup=ReplyKeyboardRemove())


def google_sheets_connector():
    """
        Connect to google sheets
        Parameters: null
        Return: sheet
    """
    print("Connecting to Google Sheets")
    scope = ['https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('key.json', scope)
    client = gspread.authorize(credentials)
    sheet = client.open('backend').sheet1
    return sheet


def get_orders_from_sheet(sheet):
    """
        Get orders from Google Sheets
        Parameters: sheet
        Return: orders list
        order: (stock name, entry, stop gain, stop partial, stop loss, flag (already bought?))
    """
    print("Getting data from Google Sheets...")
    my_orders = []
    for row in range(100):
        order = sheet.row_values(row + 2)
        if order[0] != '-':
            my_orders.append(order)
            continue
        break
    print("My orders: " + str(my_orders) + "\n")
    return my_orders


def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Até mais! Quando quiser falar novamente comigo envie /start.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    updater = Updater(token, use_context=True)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            MODE: [RegexHandler('^(Criar Ordem|Editar Ordem|Ver Ordens)$', set_mode)],
        },

        fallbacks=[CommandHandler('cancelar', cancel)]
    )

    dp.add_handler(conv_handler)
    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
