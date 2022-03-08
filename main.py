import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
import RPi.GPIO as GPIO  # puertos de raspberry
import time
from yeelight import Bulb  # Libreria para foco MI
from w1thermsensor import W1ThermSensor, Unit
import numpy as np
import telegram

def send_data_idb(totlit, time_s, temper):
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
    p = influxdb_client.Point("Litros").field("Litros", totlit)
    ptime = influxdb_client.Point("Tiempo").field("Segundos", time_s)
    ptemp = influxdb_client.Point("TemperaturaProm").field("Celsius", temper)
    write_api.write(bucket=bucket, org=org, record=p)
    write_api.write(bucket=bucket, org=org, record=ptime)
    write_api.write(bucket=bucket, org=org, record=ptemp)
    client.close()





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
    bulb.turn_on()  # encendemos el foco
    bulb.set_hsv(360, 0, 1)  # establecemos el color del foco en formato HSV
    bulb.set_brightness(100)  # Ajustamos el brillo al 100
    bulb.set_color_temp(6500)  # Ajustamos la temperatura del foco

    
    
def blue():
    bulb.set_rgb(0, 204, 204)
    
    
    
def red():
    bulb.set_rgb(255, 153, 153)


def Pulse_cnt(inpt_pin):
    global rate_cnt, tot_cnt
    rate_cnt += 1
    tot_cnt += 1



GPIO.setmode(GPIO.BCM)
inpt = 13
GPIO.setup(inpt, GPIO.IN)
minutos = 0
constant = 0.00210
time_new = 0.0
rpt_int = 10

global rate_cnt, tot_cnt, TotLit, LperM, tiempo, bulb
rate_cnt = 0
tot_cnt = 0
bulb = Bulb("192.168.100.96")
temperaturas = []
sensor = W1ThermSensor()
track = time.time()




GPIO.add_event_detect(inpt, GPIO.FALLING, callback=Pulse_cnt)

if __name__ == '__main__':

    # MAIN
    print("Registro de litros gastados y temperatura promedio el dia: ", str(time.asctime(time.localtime(time.time()))))
    rpt_int = int(input("\nSegundos de captar el flujo "))
    print("Control + c para salir")
    # Variables auxiliares
    auxLiters = 0
    aux1 = 0
    auxR = 0
    auxTemp = 0
    bulb.turn_on()  # encendemos el foco
    whitheBulb()
    inicio = time.time()
    while (rpt_int < 10):  # rpt_int<10 or,,or GPIO.input(inpt)==True <-- esta linea para pruebas antes de todo lo demas
        rpt_int += 1
        auxR += 1
        TotLit = round(tot_cnt * constant, 2)
        t_celsius = sensor.get_temperature()
        temperaturas.append(t_celsius)
        if (TotLit >= 10 and auxLiters == 0):
            red() # color rojo al foco
            print("Excediste de litros")
            auxLiters = 1
        if (auxLiters == 1 and auxR >=6):
            whitheBulb()#Volvemos a foco blanco
        time.sleep(1)

    final = time.time()
    time_shower = round((final - inicio), 2)
    print('Litros gastados: ', TotLit)
    print('Tiempo:  ', time_shower, ' segundos')
    GPIO.cleanup()
    bulb.turn_off()
    Temp = np.mean(temperaturas)
    idb(TotLit, time_shower, Temp)  # Llamar la función para enviar la cantidad de litros gastados
    send_alerts(TotLit, time_shower, Temp)
    print("Se acabo")

