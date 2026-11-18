import pytest

from app import app


@pytest.fixture
def client():
    app.config.update(TESTING=True)
    with app.test_client() as client:
        yield client


def test_default_is_v2(client):
    response = client.get("/users/1")
    assert response.status_code == 200
    assert response.headers["X-API-Version-Served"] == "2"
    assert response.json == {
        "id": 1, "first_name": "Văn", "last_name": "Nguyễn", "email": "a@vnu.vn"
    }


@pytest.mark.parametrize("version", ["1", "2", "2024-06-20"])
def test_explicit_version_and_schema(client, version):
    response = client.get("/users/1", headers={"X-API-Version": version})
    assert response.status_code == 200
    assert response.headers["X-API-Version-Served"] == version
    assert "X-API-Version" in response.vary
    if version == "1":
        assert response.json == {"id": 1, "full_name": "Văn Nguyễn"}
    else:
        assert response.json == {
            "id": 1, "first_name": "Văn", "last_name": "Nguyễn", "email": "a@vnu.vn"
        }


@pytest.mark.parametrize("version", ["99", "", "v1", "2024-01-01"])
def test_unsupported_version_does_not_fallback(client, version):
    response = client.get("/users/1", headers={"X-API-Version": version})
    assert response.status_code == 400
    assert response.json == {"error": "unsupported version"}
    assert "X-API-Version-Served" not in response.headers


@pytest.mark.parametrize("version", ["1", "2", "2024-06-20"])
def test_missing_user_preserves_404(client, version):
    response = client.get("/users/999", headers={"X-API-Version": version})
    assert response.status_code == 404
    assert response.json == {"error": "not found"}
    assert response.headers["X-API-Version-Served"] == version
