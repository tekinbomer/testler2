from flask import Flask, request, jsonify
from flask_cors import CORS
from db import get_db
import psycopg2.extras
from pywebpush import webpush, WebPushException
import json
import traceback

# VAPID anahtarları
VAPID_PUBLIC_KEY = "BMOhjeHer31_xUhmI63P5j_nL3uhLVHr25lruI4JUQ_qqzVJbhUynQjFz7LWm7dCUtmvbhr468E-Iijoyr09c6w"
VAPID_PRIVATE_KEY = "03QgB9XbHqRZY-AdT65mwphBLZJzhustenhepCO6d1E"
VAPID_CLAIMS = {"sub": "mailto:siparis@tarotalemi.com"}

subscriptions = []

app = Flask(__name__)
CORS(app)

# ----- UTIL: ROL BAZLI BİLDİRİM FONKSİYONU -----
def notify(role, title, body, url=None):
    print(f"notify çağrıldı! rol={role}")
    print("Mevcut aboneler:", subscriptions)
    for sub in subscriptions:
        if sub.get("role") == role:
            try:
                # Endpoint'ten audience çıkar
                endpoint = sub.get("endpoint", "")
                # FCM için (Google): endpoint başı "https://fcm.googleapis.com" ile başlar
                audience = endpoint.split("/push-service")[0] if "/push-service" in endpoint else endpoint.split("/send/")[0]
                # Bazı endpointler için split("/send/")[0] kullanılabilir
                if "://" in audience:
                    audience = audience.split("/", 3)
                    audience = audience[0] + "//" + audience[2]
                vapid_claims = {
                    "sub": VAPID_CLAIMS["sub"],
                    "aud": audience
                }
                webpush(
                    subscription_info=sub,
                    data=json.dumps({"title": title, "body": body, "url": url}),
                    vapid_private_key=VAPID_PRIVATE_KEY,
                    vapid_claims=vapid_claims
                )
            except WebPushException as e:
                print("Bildirim hatası:", e)


# ----- VAPID KEY -----
@app.route("/vapid-public-key")
def get_public_key():
    return VAPID_PUBLIC_KEY

# ----- SUBSCRIBE (KURYE/ADMIN) -----
@app.route("/subscribe", methods=["POST"])
def subscribe():
    data = request.get_json()
    # endpoint+rol aynıysa tekrar ekleme
    if data and not any(sub["endpoint"] == data["endpoint"] and sub.get("role") == data.get("role") for sub in subscriptions):
        subscriptions.append(data)
    return jsonify({"status": "abone kaydedildi"})

# ----- KATEGORİLER -----
@app.route('/categories', methods=['GET'])
def list_categories():
    conn = get_db()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("SELECT * FROM categories ORDER BY id ASC")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify([dict(row) for row in rows])

# ----- ÜRÜNLER -----
@app.route('/products', methods=['GET'])
def list_products():
    conn = get_db()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("""
        SELECT p.id, p.name AS urun_adi, p.price AS fiyat, p.image_url AS resim_url, c.name AS kategori
        FROM products p
        JOIN categories c ON p.category_id = c.id
        ORDER BY c.id, p.id
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify([dict(row) for row in rows])

# ----- TÜM SİPARİŞLER -----
@app.route('/orders', methods=['GET'])
def list_orders():
    conn = get_db()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("SELECT * FROM orders ORDER BY id DESC")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify([dict(row) for row in rows])

# ----- TEK SİPARİŞ -----
@app.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    conn = get_db()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("SELECT * FROM orders WHERE id = %s", (order_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if row is None:
        return jsonify({'error': 'Sipariş bulunamadı'}), 404
    return jsonify(dict(row))

# ----- SİPARİŞ OLUŞTUR -----
@app.route('/orders', methods=['POST'])
def create_order():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Eksik veri'}), 400

        conn = get_db()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        sql = """
            INSERT INTO orders (customer, address, product, phone, note, status)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """
        values = (
            data.get('customer'),
            data.get('address'),
            data.get('product'),
            data.get('phone'),
            data.get('note'),
            'new'
        )
        cursor.execute(sql, values)
        result = cursor.fetchone()
        if result is None:
            raise Exception("ID alınamadı")
        order_id = result['id']
        conn.commit()
        cursor.close()
        conn.close()

        # Bildirim sadece adminlere
        notify("admin", "Yeni Sipariş Var", f"{data.get('customer')} için sipariş alındı: {data.get('product')}")

        return jsonify({
            'id': order_id,
            'customer': data.get('customer'),
            'address': data.get('address'),
            'product': data.get('product'),
            'phone': data.get('phone'),
            'note': data.get('note'),
            'status': 'new'
        }), 201

    except Exception as e:
        print("HATA:", traceback.format_exc())
        return jsonify({'error': 'Veritabanı hatası', 'details': str(e)}), 500

# ----- SİPARİŞ DURUMU GÜNCELLEME (ve BİLDİRİM) -----
@app.route('/orders/<int:order_id>/status', methods=['POST'])
def update_status(order_id):
    data = request.get_json()
    new_status = data.get('status')
    if not new_status:
        return jsonify({'error': 'Status eksik'}), 400

    conn = get_db()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("SELECT customer, product FROM orders WHERE id = %s", (order_id,))
    order = cursor.fetchone()
    cursor.execute("UPDATE orders SET status = %s WHERE id = %s", (new_status, order_id))
    conn.commit()
    cursor.close()
    conn.close()

    # Statüye göre bildirim
    if new_status == "kurye_cagir":
        notify("kurye", "Kurye Görevi", f"{order['customer']} siparişi için kurye çağrıldı.")
    elif new_status == "kurye_geldi":
        notify("admin", "Kurye Geldi", f"{order['customer']} siparişi için kurye geldi.")
    elif new_status == "yolda":
        notify("admin", "Sipariş Yolda", f"{order['customer']} siparişi yolda.")
    elif new_status == "teslim edildi":
        notify("admin", "Teslim Edildi", f"{order['customer']} siparişi teslim edildi.")

    return jsonify({'id': order_id, 'status': new_status})

# ----- MANUEL PUSH TESTİ (opsiyonel) -----
@app.route("/push", methods=["POST"])
def send_push():
    try:
        payload = request.get_json()
        role = payload.get("role", "admin")
        title = payload.get("title", "Test Bildirim")
        body = payload.get("body", "Test mesajı")
        notify(role, title, body)
        return jsonify({"status": "bildirim gönderildi"})
    except WebPushException as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
