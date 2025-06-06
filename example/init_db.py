import os
import psycopg2

DB_HOST = os.environ.get("PG_HOST")
DB_NAME = os.environ.get("PG_NAME")
DB_USER = os.environ.get("PG_USER")
DB_PASS = os.environ.get("PG_PASS")
DB_PORT = os.environ.get("PG_PORT", "5432")

try:
    conn = psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        port=DB_PORT
    )
    conn.autocommit = True
    cur = conn.cursor()

    # Önce diğer tabloları da sil (varsa)
    cur.execute("DROP TABLE IF EXISTS orders;")
    cur.execute("DROP TABLE IF EXISTS products;")
    cur.execute("DROP TABLE IF EXISTS categories;")

    # Sadece orders tablosunu oluştur
    cur.execute("""
        CREATE TABLE orders (
            id SERIAL PRIMARY KEY,
            customer TEXT,
            address TEXT,
            phone TEXT,
            product TEXT,
            note TEXT,
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    print("orders tablosu başarıyla oluşturuldu.")

    cur.close()
    conn.close()
except Exception as e:
    print("HATA:", e)
