import pytest


@pytest.fixture
def client():
    from app import app

    app.config.update(TESTING=True)
    with app.test_client() as client:
        yield client


@pytest.mark.parametrize("cohort", ["beta", "internal", "BETA"])
def test_cohort_routes_to_v2_even_when_percentage_is_zero(client, monkeypatch, cohort):
    import gateway

    monkeypatch.setattr(gateway, "V2_PERCENT", 0)
    response = client.post(
        "/orders", json={"account_id": "acct_1"}, headers={"X-Cohort": cohort}
    )
    assert response.status_code == 201
    assert response.headers["X-Order-Handler"] == "v2"
    assert response.json["version"] == "v2"
    assert response.json["account_id"] == "acct_1"
    assert response.json["order_id"]


@pytest.mark.parametrize("account_id", ["acct_42", "acct_99"])
def test_allow_list_routes_to_v2_even_when_percentage_is_zero(client, monkeypatch, account_id):
    import gateway

    monkeypatch.setattr(gateway, "V2_PERCENT", 0)
    response = client.post("/orders", json={"account_id": account_id})
    assert response.status_code == 201
    assert response.headers["X-Order-Handler"] == "v2"
    assert response.json["version"] == "v2"


@pytest.mark.parametrize(
    ("account_id", "percent", "expected_version", "expected_status"),
    [
        ("acct_1", 5, "v1", 200),
        ("acct_72", 5, "v2", 201),
        ("acct_1", 0, "v1", 200),
        ("acct_1", 100, "v2", 201),
        ("acct_1", 53, "v1", 200),
        ("acct_1", 54, "v2", 201),
    ],
)
def test_hash_bucket_and_rollout(
    client, monkeypatch, account_id, percent, expected_version, expected_status
):
    import gateway

    # acct_1 has bucket 53; acct_72 has bucket 3.
    monkeypatch.setattr(gateway, "V2_PERCENT", percent)
    for _ in range(2):
        response = client.post("/orders", json={"account_id": account_id})
        assert response.status_code == expected_status
        assert response.headers["X-Order-Handler"] == expected_version
        assert response.json["version"] == expected_version
        assert response.json["account_id"] == account_id
        assert response.json["order_id"]


@pytest.mark.parametrize(
    "body",
    [
        {}, [], "account", {"account_id": None}, {"account_id": 42},
        {"account_id": ""}, {"account_id": "   "},
    ],
)
def test_invalid_account_returns_400(client, body):
    response = client.post("/orders", json=body)
    assert response.status_code == 400
    assert response.json == {"error": "account_id must be a non-empty string"}
    assert "X-Order-Handler" not in response.headers
