from flask import Blueprint, jsonify, request
from sqlalchemy import func, update

from .errors import ApiError
from .extensions import db
from .models import Product
from .schemas import ProductIn, ProductOut, ProductPatch, ReserveIn

products_bp = Blueprint("products", __name__, url_prefix="/api/v1/products")


def get_product(product_id):
    return db.one_or_404(
        db.select(Product).where(Product.id == product_id, Product.archived.is_(False))
    )


def reserve_stock(product_id, qty):
    product = get_product(product_id)
    # Check and decrease in one UPDATE to prevent negative stock.
    result = db.session.execute(
        update(Product)
        .where(Product.id == product_id, Product.archived.is_(False), Product.qty_in_stock >= qty)
        .values(qty_in_stock=Product.qty_in_stock - qty)
        .execution_options(synchronize_session=False)
    )
    if result.rowcount != 1:
        raise ApiError(409, "out_of_stock", "Khong du hang trong kho.")
    db.session.refresh(product)
    return product


@products_bp.get("")
def list_products():
    try:
        page = int(request.args.get("page", 1))
        size = int(request.args.get("size", 20))
    except ValueError:
        raise ApiError(422, "validation_error", "page va size phai la so nguyen.")
    if page < 1 or not 1 <= size <= 100:
        raise ApiError(422, "validation_error", "page >= 1, size tu 1 den 100.")
    base = db.select(Product).where(Product.archived.is_(False))
    rows = db.session.scalars(base.order_by(Product.id).offset((page - 1) * size).limit(size)).all()
    total = db.session.scalar(
        db.select(func.count()).select_from(Product).where(Product.archived.is_(False))
    )
    return jsonify(items=ProductOut(many=True).dump(rows), page=page, size=size, total=total)


@products_bp.get("/<int:product_id>")
def detail_product(product_id):
    return jsonify(ProductOut().dump(get_product(product_id)))


@products_bp.post("")
def create_product():
    product = Product(**ProductIn().load(request.get_json()))
    db.session.add(product)
    db.session.commit()
    return jsonify(ProductOut().dump(product)), 201


@products_bp.patch("/<int:product_id>")
def patch_product(product_id):
    body = ProductPatch().load(request.get_json(), partial=True)
    product = get_product(product_id)
    for key, value in body.items():
        setattr(product, key, value)
    db.session.commit()
    return jsonify(ProductOut().dump(product))


@products_bp.delete("/<int:product_id>")
def delete_product(product_id):
    product = get_product(product_id)
    product.archived = True
    db.session.commit()
    return "", 204


@products_bp.post("/<int:product_id>/reserve")
def reserve_product(product_id):
    body = ReserveIn().load(request.get_json())
    product = reserve_stock(product_id, body["qty"])
    db.session.commit()
    return jsonify(ProductOut().dump(product))
