import os
from datetime import timezone
from email.utils import format_datetime, parsedate_to_datetime
from pathlib import Path

from flask import Flask, send_file

from blueprints.v1 import bp as v1_bp
from blueprints.v2 import bp as v2_bp


def create_app(test_config=None):
    app = Flask(__name__)
    app.json.ensure_ascii = False
    app.config["V1_SUNSET"] = os.getenv("V1_SUNSET", "Thu, 31 Dec 2026 23:59:59 GMT")
    if test_config:
        app.config.update(test_config)
    if app.config["V1_SUNSET"]:
        sunset = parsedate_to_datetime(app.config["V1_SUNSET"])
        if sunset.tzinfo is None:
            raise ValueError("V1_SUNSET must contain a timezone")
        app.config["V1_SUNSET"] = format_datetime(sunset.astimezone(timezone.utc), usegmt=True)

    app.register_blueprint(v1_bp, url_prefix="/api/v1/users")
    app.register_blueprint(v2_bp, url_prefix="/api/v2/users")

    @app.get("/openapi.yaml")
    def openapi_spec():
        return send_file(Path(app.root_path) / "openapi.yaml", mimetype="application/yaml")

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
