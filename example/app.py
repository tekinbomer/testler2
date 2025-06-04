from flask import Flask, request, jsonify
from flask_cors import CORS
from db import get_db
import psycopg2.extras

app = Flask(__name__)
CORS(app)

# Sipariş oluştur
@app.route('/orders', methods=['POST'])
def create_order():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'invalid request'}), 400

    conn = get_db()
    cursor = conn.cursor()

    sql = """
        INSERT INTO siparisler (musteri, adres, urun, status)
        VALUES (%s, %s, %s, %s)
        RETURNING id
    """
    values = (
        data.get('müşteri'),
        data.get('adres'),
        data.get('ürün'),
        'new'
    )
    cursor.execute(sql, values)
    order_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({
        'id': order_id,
        'müşteri': data.get('müşteri'),
        'adres': data.get('adres'),
        'ürün': data.get('ürün'),
        'status': 'new'
    }), 201

# Belirli siparişi getir
@app.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    conn = get_db()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cursor.execute("SELECT * FROM siparisler WHERE id = %s", (order_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if row is None:
        return jsonify({'error': 'not found'}), 404

    return jsonify(dict(row))

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
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("SELECT * FROM siparisler ORDER BY id DESC")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify([dict(row) for row in rows])

if __name__ == '__main__':
    app.run(debug=True)
