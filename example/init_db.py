from db import get_db

def create_orders_table():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            musteri VARCHAR(255),
            adres TEXT,
            urun VARCHAR(255),
            status VARCHAR(50) DEFAULT 'new',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    create_orders_table()
    print("✅ orders tablosu başarıyla oluşturuldu.")
