import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
import RPi.GPIO as GPIO  # puertos de raspberry
import time
from yeelight import Bulb  # Libreria para foco MI
from w1thermsensor import W1ThermSensor, Unit
import numpy as np
import telegram

def idb(totlit, time_s, temper):  # Función donde tenemos los datos para el envio de informacion a influxdb
    bucket = "Raspi"
    org = "jirs28"
    token = "wxgUhrtTvlLLy845NFBXIeJb4pdltNx83a3Rrudiynm5DtvU2hhpl25G_slzkL-43KvmeTkPIWu1wWHXfeMCsQ=="
    url = "https://us-east-1-1.aws.cloud2.influxdata.com"

    client = influxdb_client.InfluxDBClient(
        url=url,
        token=token,
        org=org
    )

    write_api = client.write_api(write_options=SYNCHRONOUS)
    p = influxdb_client.Point("Litros por baño").field("Litros", totlit)
    ptime = influxdb_client.Point("Tiempo por baño").field("Segundos", time_s)
    ptemp = influxdb_client.Point("Temperatura promedio").field("Celsius", temper)
    write_api.write(bucket=bucket, org=org, record=p)
    write_api.write(bucket=bucket, org=org, record=ptime)
    write_api.write(bucket=bucket, org=org, record=ptemp)
    print("Data Sended")




def send_alerts(lit, timeS, tempe):
    api_key = '5225831499:AAH-0_bNem_7_fhM0exw1Mx_tWozVVjlU64'
    user_id = '@RgaderaBot'
    fechB = time.strftime("%x")
    horaB = time.strftime("%X")

    bot = telegram.Bot(token=api_key)
    msg = ('Reporte de uso de la regadera el dia: '+fechB, 'a la hora: '+horaB)
    bot.send_message(chat_id=user_id, text=msg)
    bot.send_message(chat_id=user_id, text='Litros: ' + str(lit))
    bot.send_message(chat_id=user_id, text='Tiempo: ' + str(timeS))
    bot.send_message(chat_id=user_id, text='Temperatura promedio: ' + str(tempe))

    


def light_color_w():
    bulb.turn_on()  # encendemos el foco
    bulb.set_hsv(360, 0, 1)  # establecemos el color del foco en formato HSV
    bulb.set_brightness(100)  # Ajustamos el brillo al 100
    bulb.set_color_temp(6500)  # Ajustamos la temperatura del foco

    
    
def blue():
    track = time.time()
    bulb.set_rgb(0, 204, 204)
    
    
    
def red():
    track = time.time()
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

global rate_cnt, tot_cnt, TotLit, LperM, tiempo, aux, bulb
rate_cnt = 0
tot_cnt = 0
aux = 0
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
    bulb.turn_on()  # encendemos el foco
    bulb.set_hsv(47, 0, 1)
    bulb.set_brightness(100)
    bulb.set_color_temp(6500)
    inicio = time.time()
    while (rpt_int < 10):  # rpt_int<10 or,,or GPIO.input(inpt)==True <-- esta linea para pruebas antes de todo lo demas
        rpt_int += 1
        TotLit = round(tot_cnt * constant, 2)
        temperature_in_celsius = sensor.get_temperature()
        temperaturas.append(temperature_in_celsius)
        if time.time() + 3 > track: 
            bulb.set_rgb (255,255,255)
        if (TotLit >= 1 and aux == 0):
            red() # color rojo al foco
            print("Excediste de litros")
            aux = 1
        time.sleep(0.5)

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

