import pytest
import psycopg2
from dotenv import load_dotenv
import os

@pytest.fixture
def db_connection():
    load_dotenv()
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    yield conn
    conn.close()