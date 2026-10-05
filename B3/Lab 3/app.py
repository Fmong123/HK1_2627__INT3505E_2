import base64
import binascii
from flask import Flask, jsonify, request

app = Flask(__name__)

ORDERS = [
    {"id": 1, "status": "paid", "customer_id": 101, "total": 200},
    {"id": 2, "status": "pending", "customer_id": 102, "total": 150},
    {"id": 3, "status": "paid", "customer_id": 101, "total": 300},
    {"id": 4, "status": "cancelled", "customer_id": 103, "total": 100},
    {"id": 5, "status": "paid", "customer_id": 102, "total": 250},
    {"id": 6, "status": "pending", "customer_id": 101, "total": 200},
    {"id": 7, "status": "paid", "customer_id": 103, "total": 400},
    {"id": 8, "status": "cancelled", "customer_id": 102, "total": 180},
    {"id": 9, "status": "paid", "customer_id": 101, "total": 350},
    {"id": 10, "status": "pending", "customer_id": 103, "total": 120},
]
FIELDS = {"id", "status", "customer_id", "total"}

def make_cursor(sort, order_id):
    return base64.urlsafe_b64encode(f"{sort}:{order_id}".encode()).decode()

@app.route("/orders", methods=["GET"])
def get_orders():
    try:
        limit = int(request.args.get("limit", "5"))
        customer_id = request.args.get("customer_id")
        if customer_id is not None:
            customer_id = int(customer_id)
    except ValueError:
        return jsonify({"error": "limit and customer_id must be integers"}), 400
    if not 1 <= limit <= 100:
        return jsonify({"error": "limit must be between 1 and 100"}), 400

    status = request.args.get("status")
    orders = [
        order for order in ORDERS
        if (status is None or order["status"] == status)
        and (customer_id is None or order["customer_id"] == customer_id)
    ]

    sort = request.args.get("sort", "id")
    descending = sort.startswith("-")
    sort_field = sort[1:] if descending else sort
    if sort_field not in FIELDS:
            return jsonify({"error": "sort is invalid"}), 400
    def sort_key(order):
        return order[sort_field], order["id"]
    orders = sorted(orders, key=sort_key, reverse=descending)

    cursor = request.args.get("cursor")
    if cursor is not None:
        try:
            decoded = base64.b64decode(cursor, altchars=b"-_", validate=True).decode()
            cursor_sort, cursor_id = decoded.split(":")
            cursor_id = int(cursor_id)
            last_order = next((order for order in orders if order["id"] == cursor_id), None)
            if cursor_sort != sort or last_order is None or cursor != make_cursor(sort, cursor_id):
                raise ValueError
        except (ValueError, UnicodeError, binascii.Error):
            return jsonify({"error": "cursor is invalid"}), 400

        last_key = sort_key(last_order)
        if descending:
            orders = [order for order in orders if sort_key(order) < last_key]
        else:
            orders = [order for order in orders if sort_key(order) > last_key]

    page = orders[:limit]
    next_cursor = make_cursor(sort, page[-1]["id"]) if len(orders) > limit else None
    
    fields = request.args.get("fields")
    selected_fields = [field.strip() for field in fields.split(",")] if fields is not None else sorted(FIELDS)
    if any(field not in FIELDS for field in selected_fields):
        return jsonify({"error": "fields must include id, status, customer_id, total"}), 400
    data = [{field: order[field] for field in selected_fields} for order in page]
    return jsonify({"data": data, "next_cursor": next_cursor})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
