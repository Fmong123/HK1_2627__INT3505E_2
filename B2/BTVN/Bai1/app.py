import sqlite3
from flask import Flask, jsonify, request

app = Flask(__name__)
DB_FILE = "orders.db"

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            status TEXT NOT NULL DEFAULT 'pending',
            item TEXT NOT NULL
        )
    """
    )
    cursor.execute("SELECT COUNT(*) FROM orders")
    if cursor.fetchone()[0] == 0:
        sample_orders = [
            ("pending", "Laptop"),
            ("shipped", "Phone"),
            ("delivered", "Book"),
        ]
        cursor.executemany(
            "INSERT INTO orders (status, item) VALUES (?, ?)",
            sample_orders,
        )
        conn.commit()

    conn.close()


@app.route("/orders", methods=["GET"])
def get_orders():
    conn = get_db_connection()
    orders_rows = conn.execute("SELECT id, status, item FROM orders").fetchall()
    conn.close()
    orders_dict = {
        row["id"]: {"status": row["status"], "item": row["item"]}
        for row in orders_rows
    }
    return jsonify({"orders": orders_dict}), 200

@app.route("/orders/<oid>", methods=["GET"])
def get_order(oid):
    conn = get_db_connection()
    order_row = conn.execute("SELECT id, status, item FROM orders WHERE id = ?", (oid,)).fetchone()
    conn.close()

    if order_row is None:
        return jsonify({"error": "not found"}), 404

    return jsonify({"status": order_row["status"], "item": order_row["item"]}), 200

@app.route("/orders", methods=["POST"])
def create_order():
    data = request.get_json(silent=True) or {}
    item = data.get("item")
    if not item:
        return jsonify({"error": "need item"}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("INSERT INTO orders (item) VALUES (?)", (item,))
    conn.commit()

    new_id = cursor.lastrowid
    conn.close()

    return jsonify({"id": new_id, "order": {"status": "pending", "item": item}}), 201

@app.route("/orders/<oid>", methods=["DELETE"])
def delete_order(oid):
    conn = get_db_connection()
    order_row = conn.execute("SELECT status FROM orders WHERE id = ?", (oid,)).fetchone()

    if order_row is None:
        conn.close()
        return jsonify({"error": "not found"}), 404
    if order_row["status"] in ("shipped", "delivered"):
        conn.close()
        return jsonify({"error": "cannot delete"}), 409
    
    conn.execute("DELETE FROM orders WHERE id = ?", (oid,))
    conn.commit()
    conn.close()

    return "", 204


if __name__ == "__main__":
    init_db()  
    app.run(host="127.0.0.1", port=5000, debug=True)