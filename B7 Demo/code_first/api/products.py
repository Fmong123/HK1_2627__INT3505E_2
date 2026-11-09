from flask.views import MethodView
from flask_smorest import Blueprint

from code_first.schemas import ProductInSchema, ProductSchema
from storage import Product, db

blp = Blueprint("products", __name__, url_prefix="/products")


class ProductList(MethodView):
    @blp.arguments(ProductInSchema, required=True)
    @blp.response(201, ProductSchema)
    def post(self, data):
        product = Product(**data)
        db.session.add(product)
        db.session.commit()
        return product

    @blp.response(200, ProductSchema(many=True))
    def get(self):
        return db.session.scalars(db.select(Product).order_by(Product.id)).all()


blp.add_url_rule("", endpoint="product_list", view_func=ProductList)
