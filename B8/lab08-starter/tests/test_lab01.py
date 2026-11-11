"""LAB 1 — add your five tests here. Do not delete the smoke tests.

A. GET /books, empty database -> HTTP 200 and []
B. GET /books/9999 -> HTTP 404, JSON code == NOT_FOUND
C. POST /books with only author -> HTTP 400, errors contains title
D. POST valid book, DELETE it, GET same id -> HTTP 404
BONUS. Validate a Book response using JSON Schema; add an unknown
       field to a *copy* of the response and assert ValidationError.

Useful imports:
    from jsonschema import validate, ValidationError
    import pytest
    from tools import get_book_schema

Do not depend on test execution order. Fixtures: client, app, sample_book.
"""

import pytest
from jsonschema import ValidationError, validate

from tools import get_book_schema


def test_get_books_empty(client):
    response = client.get("/books")

    assert response.status_code == 200
    assert response.is_json
    assert response.get_json() == []


def test_get_book_not_found(client):
    response = client.get("/books/9999")

    assert response.status_code == 404
    assert response.is_json
    assert response.get_json()["code"] == "NOT_FOUND"


def test_create_book_missing_title(client):
    response = client.post("/books", json={"author": "Author"})

    assert response.status_code == 400
    payload = response.get_json()
    assert payload["code"] == "VALIDATION_ERROR"
    assert any(error["field"] == "title" for error in payload["errors"])


def test_delete_then_get_book_not_found(client):
    created = client.post("/books", json={"title": "Book", "author": "Author"})
    assert created.status_code == 201
    book_id = created.get_json()["id"]
    assert client.get(f"/books/{book_id}").status_code == 200

    deleted = client.delete(f"/books/{book_id}")
    assert deleted.status_code == 204
    assert deleted.data == b""

    response = client.get(f"/books/{book_id}")
    assert response.status_code == 404
    assert response.get_json()["code"] == "NOT_FOUND"


def test_response_extra_field_blocked(client):
    created = client.post("/books", json={
        "title": "API Design Patterns",
        "author": "J.J. Geewax",
        "year": 2021,
        "isbn": "9781617295850",
    })
    assert created.status_code == 201
    response = client.get(f"/books/{created.get_json()['id']}")
    assert response.status_code == 200
    payload = response.get_json()
    schema = get_book_schema()

    validate(instance=payload, schema=schema)
    assert "password_hash" not in payload

    extra_field_payload = {**payload, "password_hash": "fake-hash"}
    with pytest.raises(ValidationError) as exc_info:
        validate(instance=extra_field_payload, schema=schema)
    assert exc_info.value.validator == "additionalProperties"
