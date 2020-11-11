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
    if(os.getenv("LOCAL_DEV") == "true"):
        creds = ServiceAccountCredentials.from_json_keyfile_name('../client_secret.json')    
        client = gspread.authorize(creds)
        logger.info(f"G-sheets initialized")
        return client
    else:
        json_creds = os.getenv("GOOGLE_SHEETS_CREDS_JSON")
        creds_dict = json.loads(json_creds)
        creds_dict["private_key"] = creds_dict["private_key"].replace("\\\\n", "\n")
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict)
        client = gspread.authorize(creds)
        logger.info(f"G-sheets initialized")
        return client

def open_sheet(client, sn="", wn=""):
    sheet = client.open(sn).worksheet(wn)
    logger.info(f"Opened sheet:{sn} at worksheet:{wn}") 
    return sheet

#Reads data into a pandas dataframe from the current sheet
def read_data(sheet):
    df = pd.DataFrame(sheet.get_all_records())
    logger.info(f"Data read from {sheet}")
    return df

#Writes a pandas dataframe to the current sheet
def write_data(sheet,df):
    df.fillna("",inplace=True)
    try:
        sheet.update([df.columns.values.tolist()] + df.values.tolist())
        logger.info(f"Wrote data to {sheet}")
    except Exception as error:
        logger.error(f"Failed to write data becase {error}")

#Filters out any entries that do not have word(string regex) in the columns specified (col)        
def filter_df(df,col,word):
    return df[df[col].str.contains(word,na=False)]    
    
#Combines list of string cols in one col 
def combine_cols(df,cols,out):
    output = ''
    for col in cols:
       output += df[col].astype(str) + ' '
    df[out] = output.str.rstrip() #get rid of trailing space
    return df

