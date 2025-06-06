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

    # Tabloları eski haliyle sil
    cur.execute("DROP TABLE IF EXISTS orders;")
    cur.execute("DROP TABLE IF EXISTS products;")
    cur.execute("DROP TABLE IF EXISTS categories;")

    # Kategori tablosu
    cur.execute("""
        CREATE TABLE categories (
            id SERIAL PRIMARY KEY,
            name TEXT UNIQUE
        );
    """)

    # Ürün tablosu (kategoriye bağlı)
    cur.execute("""
        CREATE TABLE products (
            id SERIAL PRIMARY KEY,
            name TEXT,
            price NUMERIC(10,2),
            image_url TEXT,
            category_id INTEGER REFERENCES categories(id)
        );
    """)

    # Sipariş tablosu (ürünler burada string olarak tutulacak)
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

    print("Tüm tablolar başarıyla oluşturuldu.")

    # ÖRNEK kategori ve ürün ekle (ilk kullanıma hazır olsun)
    cur.execute("INSERT INTO categories (name) VALUES ('Ana Menü'), ('Tatlılar'), ('İçecekler');")
    cur.execute("INSERT INTO products (name, price, image_url, category_id) VALUES" +
        "('Pizza', 120, 'https://tekinservis.com/pizza.jpg', (SELECT id FROM categories WHERE name='Ana Menü'))," +
        "('Kola', 30, 'https://tekinservis.com/kola.jpg', (SELECT id FROM categories WHERE name='İçecekler'))," +
        "('Cheesecake', 60, 'https://tekinservis.com/cheesecake.jpg', (SELECT id FROM categories WHERE name='Tatlılar'));"
    )

    print("Örnek kategoriler ve ürünler eklendi.")

    cur.close()
    conn.close()
except Exception as e:
    print("HATA:", e)
