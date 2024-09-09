import requests
import json
import pandas as pd
import api_token as a

# Define your request headers with the custom API token
headers = {
  "x-moz-token": a.API_TOKEN
}

f_input='input/domains.csv'
domains=pd.read_csv(f_input,header=None)
url = "https://lsapi.seomoz.com/v2/url_metrics"
data = {
    "targets": domains[0].to_list()
}
# Convertir el diccionario en una cadena JSON
json_data = json.dumps(data, indent=2)

response = requests.post(url, data=json_data, headers=headers)

# Verificar si la solicitud fue exitosa
if response.status_code == 200:
    # Nombre del archivo en el que deseas guardar la cadena
    nombre_archivo = "output/aux.txt"
    # Abrir el archivo en modo escritura y guardar la cadena
    with open(nombre_archivo, "w") as archivo:
        archivo.write(response.text)
    data_json = response.json()
    if data_json.get('results')!=None:
        dct_arr=[]
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
        df = pd.DataFrame(dct_arr)
        df.to_csv('output/moz_data.csv', mode='a', header=False, index=False)
else:
    print(f"Error: {response.status_code}, {response.text}")

