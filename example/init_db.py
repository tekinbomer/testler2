import psycopg2
from db import get_db

conn = get_db()
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS orders")

cursor.execute("""
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    musteri TEXT NOT NULL,
    adres TEXT NOT NULL,
    urun TEXT NOT NULL,
    status TEXT DEFAULT 'new'
)
""")

conn.commit()
cursor.close()
conn.close()

print("✅ orders tablosu sıfırlandı ve yeniden oluşturuldu.")
