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

# returns date, mm_dd_yyyy format, where _ is determined by sep, number_of_days days ago or from today's date, depending on past_or_future
def get_date_from_today(sep, number_of_days, past_or_future):
    today = date.today()

    if past_or_future == "future":
        return_date = today + timedelta(days=number_of_days)
    else:
        return_date = today - timedelta(days=number_of_days)

    return return_date.strftime(f"%-m{sep}%-d{sep}%Y")

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
    seven_days_ago = get_date_from_today("/", 7, "past")
    parse_filings_on_cloud(seven_days_ago, date.today().strftime(f"%-m/%-d/%Y"))

def scrape_settings():
    ninety_days_later = get_date_from_today("-", 90, "future")
    seven_days_ago = get_date_from_today("-", 7, "past")
    parse_settings_on_cloud(seven_days_ago, ninety_days_later)

def scrape_filings_and_settings_task():
    perform_task_and_catch_errors(scrape_filings, "Scraping filings")
    perform_task_and_catch_errors(scrape_settings, "Scraping settings")

# scrape filings and settings every Monday at 3:00 A.M. EST
if __name__ == "__main__":
    sched = BlockingScheduler()
    sched.add_job(scrape_filings_and_settings_task, 'interval', days=1, start_date='2020-11-08 22:40:00', timezone='US/Eastern')
    sched.start()
