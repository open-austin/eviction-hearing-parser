import os
import sys
import json
import gspread
import logging
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger()
logging.basicConfig(stream=sys.stdout)
logger.setLevel(logging.INFO)



if __name__ == "__main__":
    # use creds to create a client to interact with the Google Drive API
    #scope = ['https://spreadsheets.google.com/feeds']
    json_creds = os.getenv("GOOGLE_SHEETS_CREDS_JSON")
    creds_dict = json.loads(json_creds)
    creds_dict["private_key"] = creds_dict["private_key"].replace("\\\\n", "\n")
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict)
    client = gspread.authorize(creds)
    
    # Find a workbook by name and open the first sheet
    # Make sure you use the right name here.
    sheet = client.open("Court_scraper_backend").sheet1
    
    # Extract and print all of the values
     
    logger.info(f"{sheet.get_all_values()}")
