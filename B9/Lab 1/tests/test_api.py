from copy import deepcopy
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft4Validator
from openapi_spec_validator import validate

from app import create_app
from blueprints.users_data import USERS


@pytest.fixture
def client():
    original = deepcopy(USERS)
    app = create_app({"TESTING": True})
    with app.test_client() as client:
        yield client
    USERS.clear()
    USERS.update(original)


def test_versioned_schemas_and_sunset(client):
    v1 = client.get("/api/v1/users/1")
    v2 = client.get("/api/v2/users/1")
    assert v1.status_code == v2.status_code == 200
    assert v1.json == {"id": 1, "full_name": "Văn Nguyễn", "email": "a@vnu.vn"}
    assert v2.json == {
        "id": 1, "first_name": "Văn", "last_name": "Nguyễn", "email": "a@vnu.vn"
    }
    assert v1.headers["Sunset"] == "Thu, 31 Dec 2026 23:59:59 GMT"
    assert "Sunset" not in v2.headers


@pytest.mark.parametrize("version", ["v1", "v2"])
def test_unknown_user(client, version):
    response = client.get(f"/api/{version}/users/999")
    assert response.status_code == 404
    assert response.json == {"error": "nf"}
    assert ("Sunset" in response.headers) == (version == "v1")


def test_create_shared_user_and_unique_ids(client):
    data = {"first_name": " Linh ", "last_name": "Phạm", "email": "linh@vnu.vn"}
    response = client.post("/api/v2/users", json=data)
    assert response.status_code == 201
    assert "Sunset" not in response.headers
    assert response.json == {
        "id": 3, "first_name": "Linh", "last_name": "Phạm", "email": "linh@vnu.vn"
    }
    assert response.headers["Location"] == "/api/v2/users/3"
    assert client.get(response.headers["Location"]).json == response.json
    assert client.get("/api/v1/users/3").json["full_name"] == "Linh Phạm"
    assert client.post("/api/v2/users", json=data).json["id"] == 4
    assert client.post("/api/v1/users", json=data).status_code == 404


@pytest.mark.parametrize("body", [
    None, [], {},
    {"first_name": "A", "last_name": "B"},
    {"first_name": " ", "last_name": "B", "email": "a@b"},
    {"first_name": 1, "last_name": "B", "email": "a@b"},
    {"first_name": "A", "last_name": "B", "email": "invalid"},
    {"first_name": "A", "last_name": "B", "email": "a@@b"},
    {"first_name": "A", "last_name": "B", "email": "a@b", "id": 99},
])
def test_invalid_input_does_not_create_users(client, body):
    import json

    response = client.post("/api/v2/users", data=json.dumps(body), content_type="application/json")
    assert response.status_code == 400
    assert "error" in response.json
    assert len(USERS) == 2


def test_malformed_json_and_wrong_content_type(client):
    assert client.post("/api/v2/users", data="{", content_type="application/json").status_code == 400
    assert client.post("/api/v2/users", data="text").status_code == 415


def test_sunset_can_be_disabled():
    client = create_app({"TESTING": True, "V1_SUNSET": ""}).test_client()
    assert "Sunset" not in client.get("/api/v1/users/1").headers


def test_openapi_and_response_contracts(client):
    spec = yaml.safe_load((Path(__file__).resolve().parents[1] / "openapi.yaml").read_text(encoding="utf-8"))
    validate(spec)
    assert client.get("/openapi.yaml").status_code == 200
    for version, schema_name in [("v1", "UserV1"), ("v2", "UserV2")]:
        schema = {"$ref": f"#/components/schemas/{schema_name}", "components": spec["components"]}
        Draft4Validator(schema).validate(client.get(f"/api/{version}/users/1").json)
