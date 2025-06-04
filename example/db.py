import os
import psycopg2
from psycopg2.extras import RealDictCursor

def get_db():
    return psycopg2.connect(
        host=os.getenv("PG_HOST"),
        database=os.getenv("PG_NAME"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASS"),
        port=int(os.getenv("PG_PORT")),  # <-- düzeltme burada
        cursor_factory=RealDictCursor
    )

