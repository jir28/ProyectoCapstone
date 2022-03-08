import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
import RPi.GPIO as GPIO  # puertos de raspberry
import time
from yeelight import Bulb  # Libreria para foco MI
from w1thermsensor import W1ThermSensor, Unit
import numpy as np
import telegram

def send_data_idb(totlit, time_s, temper):
    LITERS = int(totlit)
    TIEMPO =int(time_s)
    TEMPER = int(temper)
    bucket = "ShowerS"
    org = "jirs28"
    token = "CogeqAhxfHt5o-0rkeCtKiMxyhXMjJaqugbHUN_LisF7cvH9LaIyDvFAZfU5CEDVrFkiYeh_69_TQ-NKUsKCeg=="
    url = "https://us-east-1-1.aws.cloud2.influxdata.com"

    client = influxdb_client.InfluxDBClient(
        url=url,
        token=token,
        org=org
    )

    write_api = client.write_api(write_options=SYNCHRONOUS)
    p = influxdb_client.Point("Litros").field("Litros", LITERS)
    ptime = influxdb_client.Point("Tiempo").field("Segundos", TIEMPO)
    ptemp = influxdb_client.Point("TemperaturaProm").field("Celsius", TEMPER)
    write_api.write(bucket=bucket, org=org, record=p)
    write_api.write(bucket=bucket, org=org, record=ptime)
    write_api.write(bucket=bucket, org=org, record=ptemp)
    client.close()


def BienvenidaMsg(msg):
    api_key = '5225831499:AAH-0_bNem_7_fhM0exw1Mx_tWozVVjlU64'
    user_id = '@RgaderaBot'
    bot = telegram.Bot(token=api_key)
    bot.send_message(chat_id=user_id, text=msg)


def send_alerts(lit, timeS, tempe):
    api_key = '5225831499:AAH-0_bNem_7_fhM0exw1Mx_tWozVVjlU64'
    user_id = '@RgaderaBot'
    fechB = time.strftime("%x")
    horaB = time.strftime("%X")

    bot = telegram.Bot(token=api_key)
    msg = ('Reporte de uso de la regadera el dia: '+fechB, 'a la hora: '+horaB)
    bot.send_message(chat_id=user_id, text=msg)
    bot.send_message(chat_id=user_id, text='Usaste ' + str(lit)+ ' litros')
    bot.send_message(chat_id=user_id, text='Tu baño duro  ' + str(timeS)+' minutos')
    bot.send_message(chat_id=user_id, text='Temperatura promedio: ' + str(tempe)+' grados Celsius')

    


def whitheBulb():
    bulb.set_hsv(360, 0, 1)  # establecemos el color del foco en formato HSV
    bulb.set_brightness(100)  # Ajustamos el brillo al 100
    bulb.set_color_temp(6500)  # Ajustamos la temperatura del foco

    
    
def blue():
    bulb.set_rgb(0, 204, 204)
    bulb.set_brightness(100)  # Ajustamos el brillo al 100
    
    
def red():
    bulb.set_rgb(255, 153, 153)
    bulb.set_brightness(100)  # Ajustamos el brillo al 100



def Pulse_cnt(inpt_pin):
    global rate_cnt, tot_cnt
    rate_cnt += 1
    tot_cnt += 1



GPIO.setmode(GPIO.BCM)
inpt = 13
GPIO.setup(inpt, GPIO.IN)
time_new = 0.0
rpt_int = 10


global rate_cnt, tot_cnt, TotLit, LperM, tiempo, bulb, inicio,check
rate_cnt = 0
tot_cnt = 0
bulb = Bulb("192.168.100.96")
inicio = 0
temperaturas = []
sensor = W1ThermSensor()




GPIO.add_event_detect(inpt, GPIO.FALLING, callback=Pulse_cnt)

def flujo():
    inicio = 0
    check = 1
    constant = 0.00210
    auxmsg = 0
    litros = round(tot_cnt * constant, 5) 
    msgWelcome = 'Smart Shower te da la bienvenida a tu baño inteligente'
    print(litros)
    auxColor = 0
    auxct = 0
    while litros > 0:  # rpt_int<10 or,,or GPIO.input(inpt)==True <-- esta linea para pruebas antes de todo lo demas
        if (auxmsg == 0):

            inicio = time.time()
            bulb.turn_on()  # encendemos el foco
            whitheBulb()
            BienvenidaMsg(msgWelcome)
            auxmsg = 1
        auxTime = 0
        TotLit = round((tot_cnt * constant) , 5)
        t_celsius = sensor.get_temperature()
        temperaturas.append(t_celsius)

        if (TotLit >= 1 and TotLit < 1.9 and auxColor == 0):
            blue() # color rojo al foco
            auxColor = 1

        if(t_celsius > 10 and auxct == 0):
            red()
            auxct = 1

        elif(TotLit >= 2 and auxColor == 1):
            whitheBulb()  
            auxColor = 4

        if(check - TotLit == 0):
            final = time.time()
            time_shower = round((final - inicio)/60, 2)
            GPIO.cleanup()
            Temp = round(np.mean(temperaturas),2)
            send_data_idb(TotLit, time_shower, Temp)  # Llamar la función para enviar la cantidad de litros gastados
            send_alerts(TotLit, time_shower, Temp)
            return 5
        time.sleep(0.99)
        check = TotLit # no borrar
    return 3

    
