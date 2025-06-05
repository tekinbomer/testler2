

# Doğru:
from vapid_key import generate_vapid_keys


# altına bu fonksiyonu çağır:
print(generate_vapid_keys())


from flask import Flask, request, jsonify
from flask_cors import CORS
from db import get_db
import psycopg2.extras

app = Flask(__name__)
CORS(app)

# Sipariş oluştur
from flask import Flask, request, jsonify
from flask_cors import CORS
from db import get_db
import psycopg2.extras
import traceback  # ← bu satırı ekle

app = Flask(__name__)
CORS(app)

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
            INSERT INTO orders (customer, address, product, status)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """
        values = (
            data.get('customer'),
            data.get('address'),
            data.get('product'),
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

        return jsonify({
            'id': order_id,
            'customer': data.get('customer'),
            'address': data.get('address'),
            'product': data.get('product'),
            'status': 'new'
        }), 201

    except Exception as e:
        print("HATA:", traceback.format_exc())  # ← logu detaylı bas
        return jsonify({'error': 'Veritabanı hatası', 'details': str(e)}), 500


# Siparişi getir
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

# Sipariş güncelle
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

# Tüm siparişleri listele
@app.route('/orders', methods=['GET'])
def list_orders():
    conn = get_db()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("SELECT * FROM orders ORDER BY id DESC")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify([dict(row) for row in rows])

if __name__ == '__main__':
    app.run(debug=True)
