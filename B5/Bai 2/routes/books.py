import base64
import binascii
import json
from pathlib import Path

from flask import Blueprint, jsonify, request
from jsonschema import ValidationError, validate
from sqlalchemy import and_, or_
from sqlalchemy.exc import IntegrityError

from models import Book, Category, db

bp = Blueprint("books", __name__)
SCHEMA = json.loads(
    (Path(__file__).resolve().parents[1] / "schemas" / "book.json").read_text(encoding="utf-8")
)
SORT = {"id": Book.id, "price": Book.price_vnd, "title": Book.title, "stock": Book.stock}


def parse_sort(raw):
    keys = []
    for part in raw.split(","):
        part = part.strip()
        name = part[1:] if part.startswith("-") else part
        if name not in SORT or name in [key for key, _ in keys]:
            raise ValueError("sort chỉ nhận id, price, title, stock; không lặp trường.")
        keys.append((name, part.startswith("-")))
    if "id" not in [name for name, _ in keys]:
        keys.append(("id", False)) 
    return keys


def encode_cursor(book, keys, genre):
    state = {
        "sort": keys,
        "genre": genre,
        "values": [getattr(book, SORT[name].key) for name, _ in keys],
    }
    return base64.urlsafe_b64encode(json.dumps(state).encode()).decode().rstrip("=")


def apply_cursor(query, token, keys, genre):
    try:
        raw = base64.b64decode(token + "=" * (-len(token) % 4), altchars=b"-_", validate=True)
        state = json.loads(raw)
        if not isinstance(state, dict):
            raise ValueError
        if state.get("sort") != [[name, desc] for name, desc in keys] or state.get("genre") != genre:
            raise ValueError
        values = state["values"]
        if not isinstance(values, list) or len(values) != len(keys):
            raise ValueError
        for (name, _), value in zip(keys, values):
            if type(value) is not (str if name == "title" else int):
                raise ValueError
    except (ValueError, KeyError, TypeError, UnicodeError, binascii.Error):
        raise ValueError("cursor không hợp lệ hoặc không khớp sort/genre.") from None

    conditions, equal_prefix = [], []
    for (name, desc), value in zip(keys, values):
        column = SORT[name]
        conditions.append(and_(*equal_prefix, column < value if desc else column > value))
        equal_prefix.append(column == value)
    return query.filter(or_(*conditions))


@bp.route("/api/v1/books", methods=["GET"])
def list_books():
    try:
        strategy = request.args.get("strategy", "offset")
        if strategy not in ("offset", "cursor"):
            raise ValueError("strategy chỉ nhận offset hoặc cursor.")
        limit = int(request.args.get("limit", 20))
        if not 1 <= limit <= 100:
            raise ValueError("limit phải từ 1 đến 100.")

        genre = request.args.get("genre", "").strip()
        keys = parse_sort(request.args.get("sort", "-id"))
        query = db.session.query(Book)
        if genre:
            query = query.join(Book.category).filter(Category.slug == genre)
        order = [SORT[name].desc() if desc else SORT[name].asc() for name, desc in keys]

        if strategy == "offset":
            if "cursor" in request.args:
                raise ValueError("cursor chỉ dùng với strategy=cursor.")
            offset = int(request.args.get("offset", 0))
            if offset < 0:
                raise ValueError("offset phải >= 0.")
            total = query.count()
            books = query.order_by(*order).offset(offset).limit(limit).all()
            pagination = {
                "strategy": strategy, "offset": offset, "limit": limit,
                "total": total, "has_next": offset + limit < total,
            }
        else:
            if "offset" in request.args:
                raise ValueError("offset chỉ dùng với strategy=offset.")
            if "cursor" in request.args:
                query = apply_cursor(query, request.args["cursor"], keys, genre)
            rows = query.order_by(*order).limit(limit + 1).all()
            books, has_more = rows[:limit], len(rows) > limit
            pagination = {
                "strategy": strategy, "limit": limit, "has_more": has_more,
                "next_cursor": encode_cursor(books[-1], keys, genre) if has_more else None,
            }
        return jsonify({"data": [book.to_dict() for book in books], "pagination": pagination})
    except ValueError as error:
        return jsonify({"error": str(error)}), 400


@bp.route("/api/v1/books", methods=["POST"])
def create_book():
    data = request.get_json(silent=True)
    try:
        validate(data, SCHEMA)
    except ValidationError as error:
        return jsonify({"error": error.message}), 400

    category = db.session.query(Category).filter_by(slug=data["genre"]).first()
    if category is None:
        category = Category(name=data["genre"], slug=data["genre"])
    book = Book(
        title=data["title"], isbn=data["isbn"], price_vnd=data["price"],
        stock=data.get("stock", 0), category=category,
    )
    db.session.add(book)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "ISBN đã tồn tại."}), 409
    return jsonify(book.to_dict()), 201
