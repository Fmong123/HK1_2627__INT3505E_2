from flask import Flask, jsonify
app = Flask(__name__)
ORDERS = {
    "order_1": {"status": "pending", "item": "Laptop"},
    "order_2": {"status": "shipped", "item": "Phone"},
    "order_3": {"status": "delivered", "item": "Book"}
}

@app.route("/orders", methods=["GET"])
def get_orders():
    return jsonify({"orders": ORDERS}), 200

def get_order(order_id):
    order = ORDERS.get(order_id)
    if order is None:
        return jsonify({"error": "not found"}), 404
    return jsonify(order), 200

@app.route("/orders/<id>", methods=["DELETE"])
def delete_order(order_id): 
    order = ORDERS.get(order_id)

# 404 — không tìm thấy
    if order is None:
        return jsonify({"error": "not found"}), 404
# 409 — business rule
    if order["status"] in ("shipped", "delivered"):
        return jsonify({"error": "cannot delete"}), 409
    ORDERS.pop(order_id, None)
# 204 — success, no body
    return "", 204

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)