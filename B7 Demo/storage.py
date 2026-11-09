from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

db = SQLAlchemy()


class Product(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    sku: Mapped[str] = mapped_column(String(32))
    name: Mapped[str] = mapped_column(String(255))
    price_cents: Mapped[int] = mapped_column(Integer)

    def to_dict(self):
        return {
            "id": self.id,
            "sku": self.sku,
            "name": self.name,
            "price_cents": self.price_cents,
        }


def init_storage(app, database_uri):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_uri
    db.init_app(app)
    with app.app_context():
        db.create_all()
