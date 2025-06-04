from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Basit bellek içi veri deposu
orders = {}

@app.route('/orders', methods=['POST'])
def create_order():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'invalid request'}), 400
    order_id = len(orders) + 1
    data['id'] = order_id
    data['status'] = 'new'
    orders[order_id] = data
    return jsonify(data), 201

@app.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    order = orders.get(order_id)
    if not order:
        return jsonify({'error': 'not found'}), 404
    return jsonify(order)

@app.route('/orders/<int:order_id>/status', methods=['POST'])
def update_status(order_id):
    order = orders.get(order_id)
    if not order:
        return jsonify({'error': 'not found'}), 404
    data = request.get_json() or {}
    status = data.get('status')
    if not status:
        return jsonify({'error': 'status required'}), 400
    order['status'] = status
    return jsonify(order)

if __name__ == '__main__':
    app.run(debug=True)
