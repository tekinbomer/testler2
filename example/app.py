from flask import Flask, request, jsonify
from flask_cors import CORS
from db import get_db
import psycopg2.extras
import traceback
from pywebpush import webpush, WebPushException

# VAPID anahtarları (kendi değerlerinle doldur)
VAPID_PUBLIC_KEY = "BMOhjeHer31_xUhmI63P5j_nL3uhLVHr25lruI4JUQ_qqzVJbhUynQjFz7LWm7dCUtmvbhr468E-Iijoyr09c6w"
VAPID_PRIVATE_KEY = "03QgB9XbHqRZY-AdT65mwphBLZJzhustenhepCO6d1E"
VAPID_CLAIMS = {
    "sub": "mailto:siparis@tarotalemi.com"
}

# Geçici olarak abone listesi bellekte tutulur
subscriptions = []

app = Flask(__name__)
CORS(app)

# VAPID public key'i istemciye ver
@app.route("/vapid-public-key")
def get_public_key():
    return VAPID_PUBLIC_KEY

# Kullanıcı abone olur (Web Push)
@app.route("/subscribe", methods=["POST"])
def subscribe():
    data = request.get_json()
    if data and data not in subscriptions:
        subscriptions.append(data)
    return jsonify({"status": "abone kaydedildi"})

# Tüm siparişleri getir
@app.route('/orders', methods=['GET'])
def list_orders():
    conn = get_db()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("SELECT * FROM orders ORDER BY id DESC")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify([dict(row) for row in rows])

# Belirli bir siparişi getir
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

# Sipariş oluştur
@app.route('/orders', methods=['POST'])
def create_order():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Eksik veri'}), 400

        conn = get_db()
        cursor = conn.cursor()

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

        # Yeni sipariş bildirimi
        title = "Yeni Sipariş Var"
        body = f"{data.get('customer')} için sipariş alındı: {data.get('product')}"
        for sub in subscriptions:
            try:
                webpush(
                    subscription_info=sub,
                    data=jsonify({"title": title, "body": body}).get_data(as_text=True),
                    vapid_private_key=VAPID_PRIVATE_KEY,
                    vapid_claims=VAPID_CLAIMS
                )
            except WebPushException as e:
                print("Bildirim hatası:", e)

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

# Sipariş durumunu güncelle
@app.route('/orders/<int:order_id>/status', methods=['POST'])
def update_status(order_id):
    data = request.get_json()
    new_status = data.get('status')
    if not new_status:
        return jsonify({'error': 'Status eksik'}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE orders SET status = %s WHERE id = %s", (new_status, order_id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'id': order_id, 'status': new_status})

# Manuel push tetikleme endpoint'i (isteğe bağlı)
@app.route("/push", methods=["POST"])
def send_push():
    try:
        payload = request.get_json()
        title = payload.get("title", "Yeni Sipariş Var!")
        body = payload.get("body", "Ahmet için yeni sipariş geldi.")
        for sub in subscriptions:
            webpush(
                subscription_info=sub,
                data=jsonify({"title": title, "body": body}).get_data(as_text=True),
                vapid_private_key=VAPID_PRIVATE_KEY,
                vapid_claims=VAPID_CLAIMS
            )
        return jsonify({"status": "bildirim gönderildi"})
    except WebPushException as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
