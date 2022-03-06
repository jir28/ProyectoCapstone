import random
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
import numpy as np


def obtain():
    org = "jirs28"
    token = "CogeqAhxfHt5o-0rkeCtKiMxyhXMjJaqugbHUN_LisF7cvH9LaIyDvFAZfU5CEDVrFkiYeh_69_TQ-NKUsKCeg=="
    url = "https://us-east-1-1.aws.cloud2.influxdata.com"

    client = influxdb_client.InfluxDBClient(
        url=url,
        token=token,
        org=org
    )
    query_api = client.query_api()
    # Tiempo del baño
    queryTime = ' from(bucket:"ShowerS")\
    |> range(start: -30d)\
    |> filter(fn:(r) => r._measurement == "Tiempo")\
    |> filter(fn:(r) => r._field == "Segundos" ) '

    result1 = query_api.query(org=org, query=queryTime)
    arr_tiempo = []
    for table in result1:
        for record in table.records:
            arr_tiempo.append((record.get_value()))

    # Temperatura prom
    queryTemp = ' from(bucket:"ShowerS")\
        |> range(start: -30d)\
        |> filter(fn:(r) => r._measurement == "TemperaturaProm")\
        |> filter(fn:(r) => r._field == "Celsius" ) '

    result2 = query_api.query(org=org, query=queryTemp)
    arr_temperature = []
    for table in result2:
        for record in table.records:
            arr_temperature.append((record.get_value()))

    #Litros por baño
    queryLiters = ' from(bucket:"ShowerS")\
            |> range(start: -30d)\
            |> filter(fn:(r) => r._measurement == "Litros")\
            |> filter(fn:(r) => r._field == "Litros" ) '

    result3 = query_api.query(org=org, query=queryLiters)
    arr_liters = []
    for table in result3:
        for record in table.records:
            arr_liters.append((record.get_value()))

    ar_li = np.asarray(arr_liters).reshape(1, -1)
    ar_ti = np.asarray(arr_tiempo).reshape(1, -1)
    ar_temp = np.asarray(arr_temperature).reshape(1, -1)
    arrrrr = np.concatenate((ar_li, ar_ti, ar_temp))
    print(arrrrr)

    client.close()


obtain()
