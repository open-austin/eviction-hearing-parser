import os
import sys
import time
import logging
import smtplib, ssl
import connect_to_database
import pandas as pd
import gsheet
from datetime import date, timedelta
from apscheduler.schedulers.blocking import BlockingScheduler
from functools import reduce
from dotenv import load_dotenv

# need this to prevent circular import error
if __name__ == "__main__":
    from parse_filings import parse_filings_on_cloud
    from parse_settings import parse_settings_on_cloud

load_dotenv()
local_dev = os.getenv("LOCAL_DEV") == "true"

logger = logging.getLogger()
logging.basicConfig(stream=sys.stdout)
logger.setLevel(logging.INFO)

#Dumps sql table to google sheets does not work locally (need to change connect to data base to pass True)
def dump_to_sheets(sheet, worksheet, tables, filter_evictions=False):
    if os.getenv("LOCAL_DEV") != "true":
        sheet = gsheet.open_sheet(gsheet.init_sheets(), sheet, worksheet)
        dfs = []
        for table in tables:
            conn = connect_to_database.get_database_connection(local_dev)
            sql = "select * from " + table
            df = pd.read_sql_query(sql, conn)
            #Group cases with multiple events into the same case number do we want to do this it leads to columns with " , " junk
            #if table=="events": df = df.groupby("case_detail_id").fillna('').agg(', '.join).reset_index()
            dfs.append(df)
        df = reduce(lambda left,right: pd.merge(left,vright,von='case_number',vhow='outer'), dfs)
        if filter_evictions:
            gsheet.filter_df(df, 'case_type', 'Eviction')
        gsheet.write_data(sheet, df)
    else:
        logger.info("Not dumping to google sheets because LOCAL_DEV environment variable is 'true'.")

# returns date, mm_dd_yyyy format, where _ is determined by sep, number_of_days days ago or from today's date, depending on past_or_future
def get_date_from_today(sep, number_of_days, past_or_future):
    today = date.today()

    if past_or_future == "future":
        return_date = today + timedelta(days=number_of_days)
    else:
        return_date = today - timedelta(days=number_of_days)

    return return_date.strftime(f"%-m{sep}%-d{sep}%Y")

def send_email(message, subject):
    if os.getenv("ERROR_EMAIL_ADDRESS") and os.getenv("ERROR_EMAIL_ADDRESS_PASSWORD"):
        email, password = os.getenv("ERROR_EMAIL_ADDRESS"), os.getenv("ERROR_EMAIL_ADDRESS_PASSWORD")
        port, smtp_server, context  = 465, "smtp.gmail.com", ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(email, password)
            server.sendmail(email, email, f"Subject: Eviction-scraper: {subject}\n\n{message}\n")
    else:
        logger.error("Cannot send email because the necessary environment variables (ERROR_EMAIL_ADDRESS and ERROR_EMAIL_ADDRESS_PASSWORD) do not exist.")

def log_and_email(message, subject, error=False):
    if error:
        logger.error(f"{subject}:\n{message}")
    else:
        logger.info(f"{subject}:\n{message}")

    send_email(message, subject)

def perform_task_and_catch_errors(task_function, task_name, error=False):
    before = time.time()
    logger.info(f"\n{task_name}...")
    for tries in range(1, 6):
        try:
            task_function()
            logger.info(f"Finished {task_name} in {round(time.time() - before, 2)} seconds.")
            return
        except Exception as error:
            logger.error(f"Unanticipated Error {task_name} on attempt {tries} of 5:\n{str(error)}")
    log_and_email(f"{task_name} failed on every attempt. Check Heroku logs for more details.", f"{task_name} failed", error=True)

def scrape_filings():
    seven_days_ago = get_date_from_today("-", 7, "past")
    parse_filings_on_cloud(seven_days_ago, date.today().strftime(f"%-m-%-d-%Y"))

def scrape_settings():
    ninety_days_later = get_date_from_today("-", 90, "future")
    seven_days_ago = get_date_from_today("-", 7, "past")
    parse_settings_on_cloud(seven_days_ago, ninety_days_later)

def scrape_filings_and_settings_task():
    perform_task_and_catch_errors(scrape_filings, "Scraping filings")
    gsheet.dump_to_sheets('Court_scraper_filings_archive','filings_archive',['case_detail','disposition','event'])
    perform_task_and_catch_errors(scrape_settings, "Scraping settings")
    gsheet.dump_to_sheets('Court_scraper_settings_archive','settings_archive',['setting'])
    gsheet.dump_to_sheets('Court_scraper_evictions_archive','evictions_archive',['case_detail','disposition','event','setting'],True)


# scrape filings and settings every Monday at 3:00 A.M. EST
if __name__ == "__main__":
    sched = BlockingScheduler()
    sched.add_job(scrape_filings_and_settings_task, 'interval', days=1, start_date='2020-10-12 14:49:00', timezone='US/Eastern')
    sched.start()
