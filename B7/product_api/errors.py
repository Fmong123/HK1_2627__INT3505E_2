from flask import jsonify
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import HTTPException

from .extensions import db


class ApiError(Exception):
    def __init__(self, status, error, detail):
        self.status = status
        self.error = error
        self.detail = detail


def register_error_handlers(app):
    @app.errorhandler(ApiError)
    def api_error(error):
        db.session.rollback()
        return jsonify(error=error.error, detail=error.detail), error.status

    @app.errorhandler(ValidationError)
    def validation_error(error):
        db.session.rollback()
        return jsonify(error="validation_error", detail=error.messages), 422

    @app.errorhandler(IntegrityError)
    def integrity_error(error):
        db.session.rollback()
        return jsonify(error="conflict", detail="Du lieu trung hoac vi pham rang buoc."), 409

    @app.errorhandler(HTTPException)
    def http_error(error):
        db.session.rollback()
        return jsonify(error=error.name.lower().replace(" ", "_"), detail=error.description), error.code

    @app.errorhandler(Exception)
    def unexpected_error(error):
        db.session.rollback()
        app.logger.exception("Unhandled request error")
        return jsonify(error="internal_error", detail="Loi he thong."), 500
