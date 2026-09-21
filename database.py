import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    if not DATABASE_URL:
        raise RuntimeError(
            "DATABASE_URL was not found in .env"
        )

    return psycopg2.connect(DATABASE_URL)