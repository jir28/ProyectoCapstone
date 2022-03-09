import time
import influxdb_client
import numpy as np
import logging
import Solicitud

from telegram import Update, ForceReply, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

global queryTemp, queryLiters, queryTime, queryTemp7, queryLiters7, queryTime7
queryTemp = ' from(bucket:"ShowerS")\
       |> range(start: -30d)\
       |> filter(fn:(r) => r._measurement == "TemperaturaProm")\
       |> filter(fn:(r) => r._field == "Celsius" ) '

queryLiters = ' from(bucket:"ShowerS")\
            |> range(start: -30d)\
            |> filter(fn:(r) => r._measurement == "Litros")\
            |> filter(fn:(r) => r._field == "Litros" ) '

queryTime = ' from(bucket:"ShowerS")\
        |> range(start: -30d)\
        |> filter(fn:(r) => r._measurement == "Tiempo")\
        |> filter(fn:(r) => r._field == "Segundos" ) '

queryTemp7 = ' from(bucket:"ShowerS")\
       |> range(start: -7d)\
       |> filter(fn:(r) => r._measurement == "TemperaturaProm")\
       |> filter(fn:(r) => r._field == "Celsius" ) '

queryLiters7 = ' from(bucket:"ShowerS")\
            |> range(start: -7d)\
            |> filter(fn:(r) => r._measurement == "Litros")\
            |> filter(fn:(r) => r._field == "Litros" ) '

queryTime7 = ' from(bucket:"ShowerS")\
            |> range(start: -7d)\
            |> filter(fn:(r) => r._measurement == "Tiempo")\
            |> filter(fn:(r) => r._field == "Segundos" ) '

def sumValues(array_Lits):
    return round((np.sum(array_Lits)), 2)


def promT(arrTem):
    return np.mean(arrTem)


def get_data_querys():
    org = "jirs28"
    token = "CogeqAhxfHt5o-0rkeCtKiMxyhXMjJaqugbHUN_LisF7cvH9LaIyDvFAZfU5CEDVrFkiYeh_69_TQ-NKUsKCeg=="
    url = "https://us-east-1-1.aws.cloud2.influxdata.com"

    client = influxdb_client.InfluxDBClient(
        url=url,
        token=token,
        org=org
    )
    query_api = client.query_api()
    query_T = ' from(bucket:"ShowerS")\
            |> range(start: -30d)\
            |> filter(fn:(r) => r._measurement == "Litros")\
            |> filter(fn:(r) => r._field == "Litros" ) '
    aux = 0
    aux1 = 0
    aux2 = 0
    result1 = query_api.query(org=org, query=query_T)
    arr_tiempo = []
    for table in result1:
        for record in table.records:
            arr_tiempo.append((record.get_value()))
            if record.get_field() == 'Segundos' and aux == 0:
                aux = 1
            elif record.get_field() == 'Litros' and aux1 == 0:
                aux1 = 1
            elif record.get_field() == 'Celsius' and aux2 == 0:
                aux2 = 1
    client.close()
    ar_li = np.asarray(arr_tiempo).reshape(1, -1)
    if aux == 1:  # para  Tiempo
        valor = round((sumValues(ar_li)) / 60, 2)
    elif aux1 == 1:  # para Litros
        valor = sumValues(ar_li)
    elif aux2 == 1:  # para Temperatura
        valor = promT(ar_li)

    return valor


#Definimos los comandos a utilizar y sus palabras clave
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Hi {user.mention_markdown_v2()}\!',
        reply_markup=ForceReply(selective=True),
    )


def obtain():
    Lits = get_data_querys()
    return Lits
#Cuando el usario pide /reporte
def reporte (update: Update, context: CallbackContext)-> str:
    """Send a message when the command /reporte is issued."""
    reply_keyboard = [['/Semanal', '/Mensual']]#modificamos el teclado para que sólo haya dos opciones
    update.message.reply_text(
        'De cuanto tiempo te gustaria tu reporte?'
        'Semanal o Mensual',
        reply_markup = ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder='/Semana or /Mensual?'
        ),
    )
#Mensaje si el usario pide semanal
def sema_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""


    Liters = Solicitud.get_data_querys(queryLiters7)#El 7 diferencia entre ultimos 7 o 30 días
    temp = Solicitud.get_data_querys(queryTemp7)
    tiempotot = Solicitud.get_data_querys(queryTime7)
    update.message.reply_text('Litros gastados: ' + str(Liters))
    update.message.reply_text('Temperatura promedio: ' + str(temp))
    update.message.reply_text('Tiempo total de baño: ' + str(tiempotot))

#La función del mes
def mes_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""

    Liters = Solicitud.get_data_querys(queryLiters)
    temp = Solicitud.get_data_querys(queryTemp)
    tiempotot = Solicitud.get_data_querys(queryTime)
    update.message.reply_text('Litros gastados: ' + str(Liters))
    update.message.reply_text('Temperatura promedio: ' + str(temp))
    update.message.reply_text('Tiempo total de baño: ' + str(tiempotot))

#Nos ayuda a verificar que el bot funcione
def echo(update: Update, context: CallbackContext) -> None:
    """Echo the user message."""
    update.message.reply_text(update.message.text)


def main() -> None:
    """Start the bot."""
    # Actualiza el bot
    updater = Updater("5225831499:AAH-0_bNem_7_fhM0exw1Mx_tWozVVjlU64")

    # Servicio de envío
    dispatcher = updater.dispatcher

    # Definimos los diversos comandos
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("semanal", sema_command))
    dispatcher.add_handler(CommandHandler("mensual", mes_command))
    updater.dispatcher.add_handler(CommandHandler('reporte', reporte))

    # Hace echo de lo que envías
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Empieza el bot
    updater.start_polling()

    #El bot corre hasta que se haga Ctrl C
    updater.idle()

#Siempre corre
if __name__ == '__main__':
    main()