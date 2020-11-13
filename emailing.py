import os
import sys
import logging
import smtplib, ssl
from dotenv import load_dotenv

load_dotenv()
local_dev = os.getenv("LOCAL_DEV") == "true"

logger = logging.getLogger()
logging.basicConfig(stream=sys.stdout)
logger.setLevel(logging.INFO)

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
