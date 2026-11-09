from storage import Product, db


def list_products():
    rows = db.session.scalars(db.select(Product).order_by(Product.id)).all()
    return [product.to_dict() for product in rows], 200


def create_product(body):
    product = Product(**body)
    db.session.add(product)
    db.session.commit()
    return product.to_dict(), 201


def get_product(id):
    product = db.get_or_404(Product, id)
    return product.to_dict(), 200
