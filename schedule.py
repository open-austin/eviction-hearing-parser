import os
import sys
import time
import logging
import smtplib, ssl
from datetime import date, timedelta
from apscheduler.schedulers.blocking import BlockingScheduler
from parse_filings import parse_filings_on_cloud
from parse_settings import parse_settings_on_cloud
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger()
logging.basicConfig(stream=sys.stdout)
logger.setLevel(logging.INFO)


# returns yesterday's date, in mm_dd_yyyy format, where _ is determined by sep
def get_yesterday(sep):
    today = date.today()
    yesterday = today - timedelta(days=1)

    yesterday_str = yesterday.strftime(f"%-m{sep}%-d{sep}%Y")
    return yesterday_str

def send_email(message, subject):
    email, password = os.getenv("ERROR_EMAIL_ADDRESS"), os.getenv("ERROR_EMAIL_ADDRESS_PASSWORD")
    port, smtp_server, context  = 465, "smtp.gmail.com", ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(email, password)
        server.sendmail(email, email, f"Subject: {subject}\n\n{message}\n")

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
    yesterday = get_yesterday("/")
    parse_filings_on_cloud(yesterday, yesterday)

def scrape_settings():
    yesterday = get_yesterday("-")
    parse_settings_on_cloud(yesterday, yesterday)

def scrape_filings_and_settings_task():
    perform_task_and_catch_errors(scrape_filings, "Scraping filings")
    perform_task_and_catch_errors(scrape_settings, "Scraping settings")

parse_filings_on_cloud("1/1/2020", "1/10/2020")
parse_settings_on_cloud("1/1/2020", "1/10/2020")
# exit()

# scrape filings and settings every Monday at 3:00 A.M. EST
# sched = BlockingScheduler()
# sched.add_job(scrape_filings_and_settings_task, 'interval', days=1, start_date='2020-10-12 03:00:00', timezone='US/Eastern')
# sched.start()
