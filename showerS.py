import influxdb_client #Para utilizar la nube influx
from influxdb_client.client.write_api import SYNCHRONOUS #Para poder escribir infomración en nuestro bucket
import RPi.GPIO as GPIO  # puertos de raspberry
import time #Necesitamos utilizar varias funciones de tiempo para saber cuando inicia y termina
from yeelight import Bulb  # Libreria para foco MI
from w1thermsensor import W1ThermSensor, Unit # Para el sensor de temperatura
import numpy as np #Una chulada de operaciones
import telegram #Poder enviar mensajes a telegram 

def send_data_idb(totlit, time_s, temper): #La función que envía información a influx
    #Valores que vamos a escribir
    LITERS = int(totlit)
    TIEMPO =int(time_s)
    TEMPER = int(temper)
    bucket = "ShowerS" # Donde se van a guardar
    org = "jirs28"# Infopmración necesaria para identificar donde 
    token = "CogeqAhxfHt5o-0rkeCtKiMxyhXMjJaqugbHUN_LisF7cvH9LaIyDvFAZfU5CEDVrFkiYeh_69_TQ-NKUsKCeg=="
    url = "https://us-east-1-1.aws.cloud2.influxdata.com"

    client = influxdb_client.InfluxDBClient(
        url=url,
        token=token,
        org=org
    )
    #Comenzamos a escribir en la nube
    write_api = client.write_api(write_options=SYNCHRONOUS)
    p = influxdb_client.Point("Litros").field("Litros", LITERS)
    ptime = influxdb_client.Point("Tiempo").field("Segundos", TIEMPO)
    ptemp = influxdb_client.Point("TemperaturaProm").field("Celsius", TEMPER)
    write_api.write(bucket=bucket, org=org, record=p)
    write_api.write(bucket=bucket, org=org, record=ptime)
    write_api.write(bucket=bucket, org=org, record=ptemp)
    client.close()


def BienvenidaMsg(msg): #Mensaje en el canal de bienvenida
    api_key = '5225831499:AAH-0_bNem_7_fhM0exw1Mx_tWozVVjlU64'
    user_id = '@RgaderaBot'
    bot = telegram.Bot(token=api_key)
    bot.send_message(chat_id=user_id, text=msg)


def send_alerts(lit, timeS, tempe): #Resumen de banio que se manda por telegram
    api_key = '5225831499:AAH-0_bNem_7_fhM0exw1Mx_tWozVVjlU64'
    user_id = '@RgaderaBot'
    fechB = time.strftime("%x")
    horaB = time.strftime("%X")

    bot = telegram.Bot(token=api_key)
    msg = ('Reporte de uso de la regadera el dia: '+fechB, 'a la hora: '+horaB)
    bot.send_message(chat_id=user_id, text=msg)
    #Aqui enviamos nuestras tres variables, procesadas, al usuario
    bot.send_message(chat_id=user_id, text='Usaste ' + str(lit)+ ' litros')
    bot.send_message(chat_id=user_id, text='Tu baño duro  ' + str(timeS)+' minutos')
    bot.send_message(chat_id=user_id, text='Temperatura promedio: ' + str(tempe)+' grados Celsius')

    


def whitheBulb(): # Color del foco en blanco
    bulb.set_hsv(360, 0, 1)  # establecemos el color del foco en formato HSV
    bulb.set_brightness(100)  # Ajustamos el brillo al 100
    bulb.set_color_temp(6500)  # Ajustamos la temperatura del foco

    
    
def blue(): #Color del foco Azul
    bulb.set_rgb(0, 204, 204)
    bulb.set_brightness(100)  # Ajustamos el brillo al 100
    
    
def red(): #Color del foco Rojo
    bulb.set_rgb(255, 153, 153)
    bulb.set_brightness(100)  # Ajustamos el brillo al 100



def Pulse_cnt(inpt_pin): #Sensor de flujo
    global rate_cnt, tot_cnt
    rate_cnt += 1
    tot_cnt += 1


#Las entradas a la pi
GPIO.setmode(GPIO.BCM)
inpt = 13
GPIO.setup(inpt, GPIO.IN)
time_new = 0.0
rpt_int = 10

#Variables globales, es necesario hacer esto para todas las funciones puedan utilizar los datos
global rate_cnt, tot_cnt, TotLit, LperM, tiempo, bulb, inicio,check
rate_cnt = 0
tot_cnt = 0
bulb = Bulb("192.168.100.96")
inicio = 0
temperaturas = []
sensor = W1ThermSensor()




GPIO.add_event_detect(inpt, GPIO.FALLING, callback=Pulse_cnt)
#FUnción prinicpal
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
    while litros > 0:  # Espera a que haya flujo de agua para comenzar a contar el tiempo
        #Lo primero que hace cuando hay flujo es tomar una captura de la hora y enviar mensaje de bienvenida
        if (auxmsg == 0):
            inicio = time.time()
            whitheBulb()
            BienvenidaMsg(msgWelcome)
            auxmsg = 1
        auxTime = 0
        TotLit = round((tot_cnt * constant) , 5)
        t_celsius = sensor.get_temperature() #Obtenemos un valor del sensor de temperatura
        temperaturas.append(t_celsius)#Agregamos el valor a un arreglo, para poder obtener un promedio de temepratura
        
        if (TotLit >= 20 and auxColor == 0):# Si el usuario usa un garrafón de agua, el foco cambia a color azul
            blue() # color rojo al foco
            auxColor = 1

        if(t_celsius > 36 and auxct == 0): # SI el usario utiliza agua muy caliente, cambiamos a color rojo
            red()
            auxct = 1

        elif(TotLit >= 22 and auxColor == 1):# Regresamos al color blanco
            whitheBulb()  
            auxColor = 4

        if(check - TotLit == 0): #Si la cantidad de agua durante el ciclo pasado y el actual es igual, significa que ya se apagó al regadera
            final = time.time()#Obtenemos la hora en la que acaba
            time_shower = round((final - inicio)/60, 2) #Redondemaos el valor a dos decimales y hacemos la resta
            GPIO.cleanup()#borramos los valores
            Temp = round(np.mean(temperaturas),2)#Obtenemos el promedio de temepratura, gracias numpy <3
            send_data_idb(TotLit, time_shower, Temp)  # escribimos los valores en nuestro bucket de influx
            send_alerts(TotLit, time_shower, Temp) #Enviamos a telegramn
            return 5 #Salimos de este programa
        time.sleep(0.99)#para no estar capurando miles de valores por segundo
        check = TotLit # Igualamos una variable auxiliar a los litro al final del ciclo y volvemos a empezar
    return 3

    
