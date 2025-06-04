# testler2

This repository contains a small example Flask application that demonstrates a simple
integration between a restaurant system and a courier system. Orders are stored in
memory and can be created or updated via HTTP endpoints.

## Running the example

Install dependencies (Flask) and run the server:

```bash
pip install -r requirements.txt
python example/app.py
```

The server exposes the following endpoints:

- `POST /orders` – create a new order.
- `GET /orders/<id>` – get order details.
- `POST /orders/<id>/status` – update the order status (for couriers).

The example is intentionally minimal and does not persist data.
