import os
import sys
import simplejson as json
import gspread
import logging
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger()
logging.basicConfig(stream=sys.stdout)
logger.setLevel(logging.INFO)

def init_sheets():
    # use creds to create a client to interact with the Google Drive API
    if(os.getenv("LOCAL_DEV")== "true"):
        print("Local")
        creds = ServiceAccountCredentials.from_json_keyfile_name('../client_secret.json')    
        client = gspread.authorize(creds)
        logger.info("G-sheets initialized")
        return client
    else:
        json_creds = os.getenv("GOOGLE_SHEETS_CREDS_JSON")
        creds_dict = json.loads(json_creds)
        creds_dict["private_key"] = creds_dict["private_key"].replace("\\\\n", "\n")
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict)
        client = gspread.authorize(creds)
        logger.info("G-sheets initialized")
        return client

def open_sheet(client, sn="", wn=""):
    sheet = client.open(sn).worksheet(wn)
    logger.info(f"Opened sheet:{sn} at worksheet:{wn}") 
    return sheet

#Reads data into a pandas dataframe
def read_data(sheet):
    df = pd.DataFrame(sheet.get_all_records())
    logger.info("Data read from {sheet}")
    return df

#Wrties a pandas datafram to the current sheet
def write_data(sheet,df):
    sheet.update([df.columns.values.tolist()] + df.values.tolist())
    logger.info("Wrote data to {sheet}")
        
if __name__ == "__main__":
    with open('results.json', 'r') as data_file:
        json_data = data_file.read()
    data = json.loads(json_data)
    df = pd.DataFrame(data)    
    # Find a workbook by name and open the first sheet
    # Make sure you use the right name here.
    sheet = open_sheet(init_sheets(),"Court_scraper_backend","Test") 
    write_data(sheet,df)
    print(read_data(sheet))


