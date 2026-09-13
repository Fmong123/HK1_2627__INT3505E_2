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

@app.route("/orders/<order_id>", methods=["GET"])
def get_order(order_id):
    order = ORDERS.get(order_id)
    if order is None:
        return jsonify({"error": "not found"}), 404
    return jsonify(order), 200

@app.route("/orders/<order_id>", methods=["DELETE"])
def delete_order(order_id): 
    order = ORDERS.get(order_id)
    if order is None:
        return jsonify({"error": "not found"}), 404
    if order["status"] in ("shipped", "delivered"):
        return jsonify({"error": "cannot delete"}), 409
    ORDERS.pop(order_id, None)

    return "", 204

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)