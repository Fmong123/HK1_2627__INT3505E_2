import logging
from datetime import datetime, timezone

import pytest


@pytest.mark.parametrize(
    ("now", "expected_status"),
    [
        (datetime(2026, 12, 31, 23, 59, 58, tzinfo=timezone.utc), 200),
        (datetime(2026, 12, 31, 23, 59, 59, tzinfo=timezone.utc), 410),
        (datetime(2027, 1, 1, tzinfo=timezone.utc), 410),
    ],
    ids=["before-sunset", "at-sunset", "after-sunset"],
)
def test_sunset_response_and_warning(now, expected_status, monkeypatch, caplog):
    import sunset
    from app import app

    class FixedDatetime(datetime):
        @classmethod
        def now(cls, tz=None):
            return now.astimezone(tz)

    monkeypatch.setattr(sunset, "datetime", FixedDatetime)
    app.config.update(TESTING=True)

    with caplog.at_level(logging.WARNING, logger="sunset"):
        with app.test_client() as client:
            response = client.get("/api/v1/users/1")

    assert response.status_code == expected_status
    if expected_status == 200:
        assert response.json == {"id": 1, "full_name": "Nguyễn Văn A"}
        assert response.headers["Sunset"] == "Thu, 31 Dec 2026 23:59:59 GMT"
        assert response.headers["Deprecation"] == "true"
        assert response.headers["Link"] == '</api/v2/users>; rel="successor-version"'
    else:
        assert response.json == {
            "error": "gone",
            "sunset": "Thu, 31 Dec 2026 23:59:59 GMT",
            "use_instead": "/api/v2/users",
        }

    warnings = [record for record in caplog.records if record.name == "sunset"]
    assert len(warnings) == 1
    assert warnings[0].getMessage() == "deprecated_call /api/v1/users/1 127.0.0.1"
