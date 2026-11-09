import connexion
from connexion.options import SwaggerUIOptions

from storage import init_storage


def create_app(database_uri="sqlite:///design-first.sqlite"):
    app = connexion.FlaskApp(__name__, specification_dir="openapi")
    init_storage(app.app, database_uri)
    app.add_api(
        "products.yaml",
        validate_responses=True,
        swagger_ui_options=SwaggerUIOptions(swagger_ui_path="/docs"),
    )
    return app


if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=5001)
