from flask import Flask
from flask_smorest import Api

from code_first.api.products import blp
from storage import init_storage


def create_app(database_uri="sqlite:///code-first.sqlite"):
    app = Flask(__name__)
    app.config.update(
        API_TITLE="Product API - Code-first",
        API_VERSION="1.0.0",
        OPENAPI_VERSION="3.0.3",
        OPENAPI_URL_PREFIX="/",
        OPENAPI_SWAGGER_UI_PATH="/docs",
        OPENAPI_SWAGGER_UI_URL="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.32.0/",
    )
    init_storage(app, database_uri)
    Api(app).register_blueprint(blp)
    return app


if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=5002)
