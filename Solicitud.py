import influxdb_client
import numpy as np


def sumValues(array_Lits):
    return round((np.sum(array_Lits)), 2)


def promT(arrTem):
    return np.mean(arrTem)


def get_data_querys(query_infos):
    org = "jirs28"
    token = "CogeqAhxfHt5o-0rkeCtKiMxyhXMjJaqugbHUN_LisF7cvH9LaIyDvFAZfU5CEDVrFkiYeh_69_TQ-NKUsKCeg=="
    url = "https://us-east-1-1.aws.cloud2.influxdata.com"

    client = influxdb_client.InfluxDBClient(
        url=url,
        token=token,
        org=org
    )
    query_api = client.query_api()
    query_T = query_infos
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