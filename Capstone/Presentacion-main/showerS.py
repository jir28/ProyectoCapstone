import influxdb_client #Para utilizar la nube influx
from influxdb_client.client.write_api import SYNCHRONOUS #Para poder escribir infomración en nuestro bucket
import RPi.GPIO as GPIO  # puertos de raspberry
import time #Necesitamos utilizar varias funciones de tiempo para saber cuando inicia y termina
from yeelight import Bulb  # Libreria para foco MI
#from w1thermsensor import W1ThermSensor, Unit # Para el sensor de temperatura
import numpy as np #Una chulada de operaciones
import telegram #Poder enviar mensajes a telegram 
import datetime

def convert(n):
    return str(datetime.timedelta(seconds=n))


def send_data_idb(totlit, time_s, temper): #La función que envía información a influx
    bucket = "ShowerS" # Colocar el nombre del bucket de nuetra base de datos en influx
    org = "jirs28"# Nombre de la organizacion registrada en influx db
    token = "R3-V0KVD9uFYF5FhTnPiyoEaGh6ZYOF5mHkc-bZclf-TsUeDIWWaDZWKxhCmBE8BpdQqDcLxQW4d1PEvzRRH8A==" # Obtener el token dando acceso de lectura y escritura al bucket
    url = "https://us-east-1-1.aws.cloud2.influxdata.com"# URL del servidor de influx, por lo general siempre sera el mismo en caso de elegir region U.S

    client = influxdb_client.InfluxDBClient(
        url=url,
        token=token,
        org=org
    )
    # Envio de datos a influx
    write_api = client.write_api(write_options=SYNCHRONOUS)
    p = influxdb_client.Point("Litros").field("Litros", totlit)
    ptime = influxdb_client.Point("Tiempo").field("Segundos", time_s)
    ptemp = influxdb_client.Point("TemperaturaProm").field("Celsius", temper)
    write_api.write(bucket=bucket, org=org, record=p)
    write_api.write(bucket=bucket, org=org, record=ptime)
    write_api.write(bucket=bucket, org=org, record=ptemp)
    client.close()# cerramos el cliente para dejar de utilizar el servicio http que usa influx


def BienvenidaMsg(): #Mensaje en el canal de bienvenida
    msg = 'Smart Shower te da la bienvenida a tu baño inteligente'
    api_key = '5225831499:AAH-0_bNem_7_fhM0exw1Mx_tWozVVjlU64' # API key generada en telegram de nuestro bot, se obtiene con Both Father
    user_id = '@RgaderaBot' # ID del bot, con el cual podemos buscarlo
    bot = telegram.Bot(token=api_key)
    bot.send_message(chat_id=user_id, text=msg)


def send_alerts(lit, timeS, tempe): #Resumen de baño que se manda por telegram
    api_key = '5225831499:AAH-0_bNem_7_fhM0exw1Mx_tWozVVjlU64' # API key generada en telegram de nuestro bot, se obtiene con Both Father
    user_id = '@RgaderaBot' # ID del bot, con el cual podemos buscarlo
    fechB = time.strftime("%x") # obtenemos la fecha en el momento que termina de usar la regadera
    horaB = time.strftime("%X") # obtenemos la hora en el momento que termina de usar la regadera

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

def green(): #Color del foco Rojo
    bulb.set_rgb(255, 153, 153)
    bulb.set_brightness(100) 

def Pulse_cnt(inpt_pin): #Sensor de flujo
    global rate_cnt, tot_cnt
    rate_cnt += 1
    tot_cnt += 1 # Contabilizamos los litros


#Definimos el modo de uso de los puertos de la Raspberry 
GPIO.setmode(GPIO.BCM)
inpt = 13 # Definir el puerto de data donde se conectara el sensor de flujo
GPIO.setup(inpt, GPIO.IN) # Estabelcemos en modo IN el puerto del sensor de flujo
time_new = 0.0
rpt_int = 10

#Variables globales, es necesario hacer esto para todas las funciones puedan utilizar los datos
global rate_cnt, tot_cnt, TotLit, LperM, tiempo, bulb, inicio,check
rate_cnt = 0
tot_cnt = 0
bulb = Bulb("10.111.0.46")# definir la direccion IP local del foco yeelight
inicio = 0
temperaturas = []
#sensor = W1ThermSensor() # Hacemos referencia al sensor de temepratura, por defecto, la libreria W1thermsensor busca en que puerto esta conectado el sensor de temperatura




GPIO.add_event_detect(inpt, GPIO.FALLING, callback=Pulse_cnt)
#Función prinicpal
def flujo():
    inicio = 0
    check = 1
    constant = 0.00210
    auxmsg = 0
    litros = round(tot_cnt * constant, 5) 
    auxColor = 0
    auxct = 0
    auxgreen = 0
    auxG = 0
    while litros > 0:  # Espera a que haya flujo de agua para comenzar a contar el tiempo
        #Lo primero que hace cuando hay flujo es tomar una captura de la hora, enviar mensaje de bienvenida y establece el colormdel foco a blanco
        auxG +=1
        if (auxmsg == 0):
            inicio = time.time()
            whitheBulb()
            BienvenidaMsg()
            auxmsg = 1
        auxTime = 0
        TotLit = round((tot_cnt * constant) , 5) # Contabiliza los litros por cada ciclo realizado para obtener un total
        print(TotLit)
        #t_celsius = sensor.get_temperature() #Obtenemos un valor del sensor de temperatura
        #temperaturas.append(t_celsius)#Agregamos el valor a un arreglo, para poder obtener un promedio de temepratura al final


        if (TotLit >= 0.5 and auxColor == 0):# Si el usuario usa mas de 20 litros  de agua, el foco cambia a color azul
            blue() # color rojo al foco
            auxColor = 1

        #if(t_celsius > 36 and auxct == 0): # SI el usario utiliza agua muy caliente, cambiamos a color rojo
         #   red()
          #  auxct = 1

        elif(TotLit >= 2 and auxColor == 1):# Regresamos al color blanco
            whitheBulb()  
            auxColor = 4

        if(check - TotLit == 0): #Si la cantidad de agua durante el ciclo pasado y el actual es igual, significa que ya se apagó al regadera
            final = time.time()#Obtenemos la hora en la que acaba
            time_s = int((final - inicio))
            print(time_s)
            tes = 17
            time_shower = convert(time_s) #Redondeamos el valor a dos decimales y hacemos la resta para sacar el tiempo de baño en minutos
            GPIO.cleanup() # Cerramos y limpiamos los pines que usamos de la raspberry
            #Temp = round(np.mean(temperaturas),2)#Obtenemos el promedio de temepratura, gracias numpy <3
            send_data_idb(TotLit, time_s, tes)  # escribimos los valores en nuestro bucket de influx
            send_alerts(TotLit, time_shower, tes) #Enviamos a telegram la alerta con el tiempo total de litros, tiempo que duro el baño y la temperatura promedio
            return 5 #Salimos de este programa
        time.sleep(0.99)#para no estar capurando miles de valores por segundo
        check = TotLit # Igualamos una variable auxiliar a los litro al final del ciclo y volvemos a empezar
    return 3
