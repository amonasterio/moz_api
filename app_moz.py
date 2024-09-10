import requests
import json
import pandas as pd
import os
from datetime import datetime
import api_token as a


# Define your request headers with the custom API token
HEADERS = {
  "x-moz-token": a.API_TOKEN_COMPANY
}
MAX_DOMAINS=50
F_INPUT='input/domains.csv'

#Start date 'YYYY/MM/DD'
def getUsageData(start_date_str):
    rows_consumed=-1
    current_date = datetime.now()
    current_timestamp = current_date.timestamp()
    start_date = datetime.strptime(start_date_str, "%Y/%m/%d")
    # Convertir el objeto datetime a timestamp
    start_timestamp = start_date.timestamp()
    endpoint = "https://lsapi.seomoz.com/v2/usage_data"
    data = {
    "start":start_timestamp,
    "end": current_timestamp
    }
     # Convertir el diccionario en una cadena JSON
    json_data = json.dumps(data, indent=2)
    response = requests.post(endpoint, data=json_data, headers=HEADERS)
    # Verificar si la solicitud fue exitosa
    if response.status_code == 200:
        data_json = response.json()
        if data_json.get('rows_consumed')!=None:
            rows_consumed=data_json.get('rows_consumed')
    return rows_consumed

def getMozData(l_domains):
    endpoint="https://lsapi.seomoz.com/v2/url_metrics"
    data = {
    "targets": l_domains
    }
    # Convertir el diccionario en una cadena JSON
    json_data = json.dumps(data, indent=2)
    response = requests.post(endpoint, data=json_data, headers=HEADERS)
    dct_arr=[]
    # Verificar si la solicitud fue exitosa
    if response.status_code == 200:
        # Nombre del archivo en el que deseamos guardar la salida
        nombre_archivo = "output/aux.txt"
        # Abrir el archivo en modo escritura y guardar la cadena
        with open(nombre_archivo, "a",encoding='utf-8') as archivo:
            archivo.write(response.text)
        data_json = response.json()
        if data_json.get('results')!=None:
            for data in data_json['results']:     
                moz_dict={}
                moz_dict["page"]=data.get("page", None)
                moz_dict["subdomain"]=data.get("subdomain", None)
                moz_dict["root_domain"]=data.get("root_domain", None)
                moz_dict["last_crawled"]=data.get("last_crawled", None)
                moz_dict["spam_score"] = data.get("spam_score", None)
                moz_dict["page_authority"]= data.get("page_authority", None)
                moz_dict["domain_authority"] = data.get("domain_authority", None)
                print(moz_dict)
                dct_arr.append(moz_dict)
    else:
        print(f"Error: {response.status_code}, {response.text}")
    return dct_arr

ini=getUsageData('2024/09/08')
print(f'Uso inicial: ',{ini},' créditos')
domains=pd.read_csv(F_INPUT,header=None)
l_domains=domains[0].to_list()
count_domains=len(l_domains)
# Seleccionar bloques de MAX_DOMAINS elementos
domains_blocks = [l_domains[i:i+MAX_DOMAINS] for i in range(0, len(l_domains), MAX_DOMAINS)]
f_output='output/moz_data.csv'
for block in domains_blocks:
    results=getMozData(block)
    df = pd.DataFrame(results)
    #SI existe el fichero añadimos lod datos al final, si no, lo creamos
    if os.path.exists(f_output):
        df.to_csv('output/moz_data.csv', mode='a', header=False, index=False)
    else:
        df.to_csv('output/moz_data.csv', index=False)


fin=getUsageData('2024/09/08')
print(f'Uso final: ',{fin},' créditos')
diferencia=int(fin)-int(ini)
print(f'Consumidos : ',{diferencia},' créditos')