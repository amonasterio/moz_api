import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime

st.set_page_config(
   page_title="Get Moz Data"
)
st.title("Get Moz Data")

#Maximum number of domains to get Data. Request is limited to 50, but I reduce it to avoid wasting credits"
MAX_DOMAINS=10

CREDITS_MOZ=3000 #Update when the plan is modified

#It return current year and month (MM/YYYY)
def getCurrentYearMonth():
    res=""
    month = datetime.now().month
    if month<10:
        str_month="0"+str(month)
    year =  datetime.now().year
    res=str(year)+"/"+str_month
    return res

#It returns the first day of the current month (DD/MM/YYYY)
def getFirstDayCurrentMonth():
    return getCurrentYearMonth()+"/01"

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
    "start": "0", #(If no time period is specified, the results returned will reflect rows consumed so far in the current billing period
    "end":current_timestamp
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

#Get usage data. #(If no time period is specified, the results returned will reflect rows consumed so far in the current billing period)
def getUsageData():
    rows_consumed=-1
    current_date = datetime.now()
    current_timestamp = current_date.timestamp()
    endpoint = "https://lsapi.seomoz.com/v2/usage_data"
    data = {
    "start": "0", #(If no time period is specified, the results returned will reflect rows consumed so far in the current billing period)
    "end":current_timestamp
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

#Calculate the available credits, knowing the credits used
def getCreditsAvailable(credits_used):
    available=0
    if credits_used>=0:
       available=CREDITS_MOZ-creds_usage
    return available

@st.cache_data
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
                dct_arr.append(moz_dict)
    else:
       st.error(f"Error: {response.status_code}, {response.text}")
    return dct_arr

#Remove duplicate and empty elements
def removeDuplicateAndEmptyElements(array):
    empty_removed = [element for element in array if element and element.strip()]
    # Remove duplicates and preserve order
    unique_list = []
    seen = set()
    for item in empty_removed:
        if item not in seen:
            unique_list.append(item)
            seen.add(item)
    return unique_list


api_token=st.text_input("API Token")
if len(api_token)>0:
    # Define your request headers with the custom API token
    HEADERS = {
    "x-moz-token": api_token
    }
    creds_usage=getUsageData()
    st.write(str(creds_usage)+" out of 3000 credits consumed.")
    st.write(str(getCreditsAvailable(creds_usage))+" credits available.")

    text_input=st.text_area("Write the URLs or domains to obtain Moz data. We must include one domain or URL per row.\n\nMaximum of "+str(MAX_DOMAINS)+" URLs/domains.",'')

    l_domains=[]
    if len(text_input)>0:
        l_domains=text_input.split('\n')
        l_domains=removeDuplicateAndEmptyElements(l_domains)
        st.write(l_domains)
        if len(l_domains)<=MAX_DOMAINS:
            results=getMozData(l_domains)
            df = pd.DataFrame(results)    
            st.dataframe(df, hide_index=True)
            creds_usage=getUsageData()
            st.write(str(creds_usage)+" out of 3000 credits consumed.")
            st.write(str(CREDITS_MOZ-creds_usage)+" credits available.")
            st.download_button(
                label="Download CSV",
                data=df.to_csv(index = False).encode('utf-8'),
                file_name='moz_data.csv',
                mime='text/csv',
            )
    else:
        st.warning(f"We only can check up to {MAX_DOMAINS} URLs or domains")           