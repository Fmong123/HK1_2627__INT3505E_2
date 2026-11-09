import os
from pathlib import Path

import click
from flask import Flask, jsonify
from sqlalchemy import text

from .errors import register_error_handlers
from .extensions import db
from .models import Product
from .orders import orders_bp
from .products import products_bp


def create_app(config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.json.compact = False  # Pretty-print JSON responses for curl and lab screenshots.
    app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI=os.environ.get("DB_URL", "sqlite:///lab7.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )
    if config:
        app.config.update(config)
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    db.init_app(app)
    app.register_blueprint(products_bp)
    app.register_blueprint(orders_bp)
    register_error_handlers(app)

    @app.get("/healthz")
    def healthz():
        return jsonify(status="ok")

    @app.get("/ready")
    def ready():
        try:
            # Check the connection and that init-db has created the schema.
            db.session.execute(text("SELECT id FROM products LIMIT 1"))
            db.session.execute(text("SELECT id FROM orders LIMIT 1"))
            db.session.execute(text("SELECT id FROM order_items LIMIT 1"))
            return jsonify(status="ok", checks={"db": "ok"})
        except Exception:
            db.session.rollback()
            return jsonify(status="degraded", checks={"db": "error"}), 503

    @app.cli.command("init-db")
    def init_db():
        """Create missing tables without deleting existing data."""
        db.create_all()
        click.echo("Database initialized.")

    @app.cli.command("seed-db")
    def seed_db():
        """Add three sample products; existing SKUs are kept unchanged."""
        db.create_all()
        for sku, name, price, qty in [
            ("SP-001", "Ban phim", 15000, 10),
            ("SP-002", "Chuot", 8000, 20),
            ("SP-003", "Tai nghe", 20000, 5),
        ]:
            if db.session.scalar(db.select(Product).where(Product.sku == sku)) is None:
                db.session.add(Product(sku=sku, name=name, price_cents=price, qty_in_stock=qty))
        db.session.commit()
        click.echo("Sample products ready.")

    return app
