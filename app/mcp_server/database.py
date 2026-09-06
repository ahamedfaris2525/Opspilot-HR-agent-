import os

import psycopg
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    return psycopg.connect(
        host=os.getenv("DB_HOST", "db"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "opspilot"),
        user=os.getenv("DB_USER", "opspilot"),
        password=os.getenv("DB_PASSWORD", "opspilot_password"),
    )
