import streamlit as st
import pandas as pd
import requests
import json

st.set_page_config(
   page_title="Get Moz Data"
)
st.title("Get Moz Data")

#"Maximum number of domains to get Data. Request is limited to 50, but I reduce it to avoid wasting credits"
MAX_DOMAINS=10

def getMozData(l_domains):
    endpoint="https://lsapi.seomoz.com/v2/url_metrics"
    data = {
    "targets": l_domains
    }
    # Convertir el diccionario en una cadena JSON
    json_data = json.dumps(data, indent=2)
    response = requests.post(endpoint, data=json_data, headers=headers)
    dct_arr=[]
    # Verificar si la solicitud fue exitosa
    if response.status_code == 200:
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

text_input=st.text_area("Write the URLs or domains to obtain Moz data. We must include one domain or URL per row.",'')

csv=st.file_uploader('CSV with all the domains or URLs to obtain Moz data. We must include one domain or URL per row.', type='csv')

l_domains=[]
#if ther is no csv we check the text Area
if csv is None:
    if len(text_input)>0:
        l_domains=text_input.split('\n')
        st.write(l_domains)
else:
    df_input=pd.read_csv(csv,header=None)
    st.write(df_input)
    l_domains=df_input[0].to_list()
if len(l_domains)<=MAX_DOMAINS:
    api_token=st.text_input("API Token")
    if len(api_token)>0:
        # Define your request headers with the custom API token
        headers = {
        "x-moz-token": api_token
        }
        endpoint = "https://lsapi.seomoz.com/v2/url_metrics"
        data = {
            "targets": l_domains
        }
        # Convertir el diccionario en una cadena JSON
        json_data = json.dumps(data, indent=2)

        response = requests.post(endpoint, data=json_data, headers=headers)

        if response.status_code == 200:
            data_json = response.json()
            if data_json.get('results')!=None:
                dct_arr=[]
                for data in data_json['results']:     
                    moz_dict={}
                    moz_dict["page"]=data.get("page", None)
                    moz_dict["root_domain"]=data.get("root_domain", None)
                    moz_dict["spam_score"] = data.get("spam_score", None)
                    moz_dict["page_authority"]= data.get("page_authority", None)
                    moz_dict["domain_authority"] = data.get("domain_authority", None)
                    moz_dict["last_crawled"]=data.get("last_crawled", None)
                    dct_arr.append(moz_dict)
                df = pd.DataFrame(dct_arr)
                st.dataframe(df)
                st.download_button(
                    label="Download CSV",
                    data=df.to_csv(index = False).encode('utf-8'),
                    file_name='moz_data.csv',
                    mime='text/csv',
                )
        else:
            st.error(f"Error: {response.status_code}, {response.text}")
else:
    st.warning(f"We only can chac up to {MAX_DOMAINS} URLs or domains")           