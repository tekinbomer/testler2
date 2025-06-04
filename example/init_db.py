import psycopg2
from db import get_db

conn = get_db()
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS orders")

cursor.execute("""
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer TEXT NOT NULL,
    address TEXT NOT NULL,
    product TEXT NOT NULL,
    status TEXT DEFAULT 'new'
)
""")

conn.commit()
cursor.close()
conn.close()

print("✅ orders tablosu İngilizce alanlarla oluşturuldu.")
