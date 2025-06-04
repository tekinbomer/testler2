from flask import Flask, request, jsonify
from flask_cors import CORS
from db import get_db  # db.py içindeki get_db fonksiyonu

app = Flask(__name__)
CORS(app)

# Yeni sipariş oluştur
@app.route('/orders', methods=['POST'])
def create_order():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'invalid request'}), 400

    conn = get_db()
    cursor = conn.cursor()

    sql = "INSERT INTO siparisler (musteri, adres, urun, status) VALUES (%s, %s, %s, %s)"
    values = (data.get('müşteri'), data.get('adres'), data.get('ürün'), 'new')

    cursor.execute(sql, values)
    conn.commit()

    order_id = cursor.lastrowid
    cursor.close()
    conn.close()

    return jsonify({
        'id': order_id,
        'müşteri': data.get('müşteri'),
        'adres': data.get('adres'),
        'ürün': data.get('ürün'),
        'status': 'new'
    }), 201

# Sipariş bilgisi getir
@app.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM siparisler WHERE id = %s", (order_id,))
    order = cursor.fetchone()

    cursor.close()
    conn.close()

    if not order:
        return jsonify({'error': 'not found'}), 404

    return jsonify(order)

# Sipariş durumu güncelle
@app.route('/orders/<int:order_id>/status', methods=['POST'])
def update_status(order_id):
    data = request.get_json()
    new_status = data.get('status')

    if not new_status:
        return jsonify({'error': 'status required'}), 400

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("UPDATE siparisler SET status = %s WHERE id = %s", (new_status, order_id))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'id': order_id, 'status': new_status})

# Tüm siparişleri listele
@app.route('/orders', methods=['GET'])
def list_orders():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM siparisler ORDER BY id DESC")
    orders = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(orders)

if __name__ == '__main__':
    app.run(debug=True)
