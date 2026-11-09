from flask import Blueprint, jsonify, request
from sqlalchemy.orm import selectinload

from .extensions import db
from .models import Order, OrderItem
from .products import reserve_stock
from .schemas import OrderIn

orders_bp = Blueprint("orders", __name__, url_prefix="/api/v1/orders")


def order_query():
    # Two SELECTs for the list regardless of the number of orders in this lab.
    return db.select(Order).options(selectinload(Order.items).joinedload(OrderItem.product))


def serialize_order(order):
    items = [
        {
            "product_id": item.product_id,
            "product_name": item.product.name,
            "qty": item.qty,
            "unit_price_cents": item.unit_price_cents,
            "subtotal_cents": item.qty * item.unit_price_cents,
        }
        for item in order.items
    ]
    return {
        "id": order.id,
        "customer_name": order.customer_name,
        "items": items,
        "total_cents": sum(item["subtotal_cents"] for item in items),
    }


@orders_bp.get("")
def list_orders():
    orders = db.session.scalars(order_query().order_by(Order.id)).all()
    return jsonify(items=[serialize_order(order) for order in orders])


@orders_bp.get("/<int:order_id>")
def detail_order(order_id):
    order = db.one_or_404(order_query().where(Order.id == order_id))
    return jsonify(serialize_order(order))


@orders_bp.post("")
def create_order():
    body = OrderIn().load(request.get_json())
    order = Order(customer_name=body["customer_name"])
    for row in body["items"]:
        product = reserve_stock(row["product_id"], row["qty"])
        order.items.append(OrderItem(
            product=product, qty=row["qty"], unit_price_cents=product.price_cents
        ))
    db.session.add(order)
    db.session.commit()
    return jsonify(serialize_order(order)), 201
