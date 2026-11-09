import pytest
from sqlalchemy import event

from product_api import create_app
from product_api.extensions import db
from product_api.models import Order, OrderItem, Product


@pytest.fixture()
def app():
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})
    with app.app_context():
        db.create_all()
    yield app
    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


def add_product(client, sku="TEST-001", **values):
    response = client.post("/api/v1/products", json={
        "sku": sku, "name": "Ban phim", "price_cents": 1000,
        "qty_in_stock": 10, **values,
    })
    assert response.status_code == 201
    return response.json["id"]


def test_create_product_and_conflict(client):
    product_id = add_product(client)
    assert client.get(f"/api/v1/products/{product_id}").json["sku"] == "TEST-001"
    duplicate = client.post("/api/v1/products", json={
        "sku": "TEST-001", "name": "Duplicate", "price_cents": 100,
    })
    assert duplicate.status_code == 409
    assert duplicate.json["error"] == "conflict"
    # Failed transaction must not break subsequent requests.
    add_product(client, "TEST-002")


@pytest.mark.parametrize("body", [
    {}, {"sku": "AB", "name": "Test", "price_cents": 1},
    {"sku": "ABC", "name": " ", "price_cents": 1},
    {"sku": "ABC", "name": "Test", "price_cents": -1},
    {"sku": "ABC", "name": "Test", "price_cents": 1.5},
    {"sku": "ABC", "name": "Test", "price_cents": 1, "qty_in_stock": -1},
])
def test_product_validation(client, body):
    response = client.post("/api/v1/products", json=body)
    assert response.status_code == 422
    assert "detail" in response.json


def test_partial_update_pagination_and_soft_delete(client):
    first = add_product(client)
    second = add_product(client, "TEST-002")
    response = client.patch(f"/api/v1/products/{first}", json={"name": "Ten moi"})
    assert response.status_code == 200
    assert response.json["qty_in_stock"] == 10
    assert response.json["price_cents"] == 1000
    page = client.get("/api/v1/products?page=2&size=1").json
    assert (page["page"], page["size"], page["total"]) == (2, 1, 2)
    assert page["items"][0]["id"] == second
    assert client.delete(f"/api/v1/products/{first}").status_code == 204
    assert client.get(f"/api/v1/products/{first}").status_code == 404
    assert client.patch(f"/api/v1/products/{first}", json={"name": "Hidden"}).status_code == 404
    assert client.get("/api/v1/products").json["total"] == 1


@pytest.mark.parametrize("query", ["page=0", "size=101", "page=abc", "size=0"])
def test_invalid_pagination(client, query):
    assert client.get(f"/api/v1/products?{query}").status_code == 422


def test_reserve_does_not_allow_negative_stock(client):
    product_id = add_product(client, qty_in_stock=2)
    url = f"/api/v1/products/{product_id}/reserve"
    assert client.post(url, json={"qty": 0}).status_code == 422
    assert client.post(url, json={"qty": 3}).status_code == 409
    response = client.post(url, json={"qty": 2})
    assert response.status_code == 200
    assert response.json["qty_in_stock"] == 0
    assert client.post(url, json={"qty": 1}).status_code == 409
    assert client.get(f"/api/v1/products/{product_id}").json["qty_in_stock"] == 0


def test_order_multiple_items_and_price_snapshot(client):
    first = add_product(client)
    second = add_product(client, "TEST-002", price_cents=2000)
    response = client.post("/api/v1/orders", json={
        "customer_name": "Long",
        "items": [{"product_id": first, "qty": 2}, {"product_id": second, "qty": 1}],
    })
    assert response.status_code == 201
    assert len(response.json["items"]) == 2
    assert response.json["total_cents"] == 4000
    assert client.get(f"/api/v1/products/{first}").json["qty_in_stock"] == 8
    client.patch(f"/api/v1/products/{first}", json={"price_cents": 9999})
    client.delete(f"/api/v1/products/{second}")
    saved = client.get(f"/api/v1/orders/{response.json['id']}")
    assert saved.status_code == 200
    assert saved.json["total_cents"] == 4000
    assert len(saved.json["items"]) == 2


@pytest.mark.parametrize("bad_product, qty, status", [(False, 11, 409), (True, 1, 404)])
def test_failed_order_rolls_back_all_stock(client, bad_product, qty, status):
    product_id = add_product(client)
    response = client.post("/api/v1/orders", json={
        "customer_name": "Long",
        "items": [
            {"product_id": product_id, "qty": 2},
            {"product_id": 999 if bad_product else product_id, "qty": qty},
        ],
    })
    assert response.status_code == status
    assert client.get(f"/api/v1/products/{product_id}").json["qty_in_stock"] == 10
    assert client.get("/api/v1/orders").json["items"] == []


def test_get_orders_uses_eager_loading(app, client):
    with app.app_context():
        products = [Product(sku=f"P-{i:03}", name=f"Product {i}", price_cents=100, qty_in_stock=20)
                    for i in range(3)]
        for i in range(5):
            db.session.add(Order(customer_name=f"Customer {i}", items=[
                OrderItem(product=p, qty=1, unit_price_cents=100) for p in products
            ]))
        db.session.commit()
        engine = db.engine

    queries = []

    def count_select(conn, cursor, statement, parameters, context, executemany):
        if statement.lstrip().upper().startswith("SELECT"):
            queries.append(statement)

    event.listen(engine, "before_cursor_execute", count_select)
    try:
        response = client.get("/api/v1/orders")
    finally:
        event.remove(engine, "before_cursor_execute", count_select)
    assert response.status_code == 200
    assert len(response.json["items"]) == 5
    assert all(len(order["items"]) == 3 for order in response.json["items"])
    assert all(item["product_name"] for order in response.json["items"] for item in order["items"])
    assert len(queries) == 2  # orders + items JOIN products; no N+1.


def test_health_probes_when_db_unavailable(app, client):
    assert client.get("/healthz").status_code == 200
    assert client.get("/ready").status_code == 200
    with app.app_context():
        db.drop_all()
    assert client.get("/healthz").status_code == 200
    assert client.get("/ready").status_code == 503


def test_bad_json_and_missing_resource(client):
    response = client.post("/api/v1/products", data="{broken", content_type="application/json")
    assert response.status_code == 400
    assert "error" in response.json
    assert client.get("/api/v1/products/999").status_code == 404
    assert client.get("/api/v1/orders/999").status_code == 404


def test_seed_command_can_be_repeated(app, client):
    runner = app.test_cli_runner()
    assert runner.invoke(args=["init-db"]).exit_code == 0
    assert runner.invoke(args=["seed-db"]).exit_code == 0
    assert runner.invoke(args=["seed-db"]).exit_code == 0
    assert client.get("/api/v1/products").json["total"] == 3
