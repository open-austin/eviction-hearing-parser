import os
import psycopg2
from dotenv import load_dotenv
load_dotenv()

def get_database_connection(local_dev=True):
    if local_dev:
        conn = psycopg2.connect(os.getenv("LOCAL_DATABASE_URL"))
    else:
        conn = psycopg2.connect(os.getenv("DATABASE_URL"))

    return conn
