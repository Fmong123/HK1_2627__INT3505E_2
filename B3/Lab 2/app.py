import uuid

from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException

app = Flask(__name__)
ERROR_BASE = "https://API.com/problems"


class ApiProblem(Exception):
    def __init__(self, status, title, detail=None, type_path=None, **extra):
        super().__init__(detail)
        self.status = status
        self.title = title
        self.detail = detail
        self.type_path = type_path
        self.extra = extra


def _problem(status, title, detail=None, type_path=None, **extra):
    body = {
        "type": f"{ERROR_BASE}/{type_path}" if type_path else "about:blank",
        "title": title,
        "detail": detail,
        "status": status,
        "instance": request.path,
        "trace_id": str(uuid.uuid4()),
    }
    body.update(extra)

    resp = jsonify(body)
    resp.status_code = status
    resp.headers["Content-Type"] = "application/problem+json"
    return resp


@app.errorhandler(ApiProblem)
def handle_problem(error):
    return _problem(
        error.status, error.title, error.detail, error.type_path, **error.extra
    )


@app.errorhandler(HTTPException)
def handle_http(error):
    detail = error.description
    if error.code >= 500:
        app.logger.exception("HTTP server error")
        detail = "An unexpected error occurred."
    resp = _problem(error.code, error.name, detail)
    for name, value in error.get_headers():
        if name.lower() not in ("content-type", "content-length"):
            resp.headers.add(name, value)
    return resp


@app.errorhandler(Exception)
def handle_unexpected(error):
    app.logger.exception("Unhandled exception")
    return _problem(
        500, "Internal Server Error", "An unexpected error occurred."
    )


@app.get("/resources/<int:resource_id>")
def get_resource(resource_id):
    raise ApiProblem(
        status=404,
        title="Resource not found",
        detail=f"Resource {resource_id} not found.",
        type_path="resource-not-found",
        resource_id=resource_id,
    )


@app.get("/crash")
def crash():
    raise RuntimeError("Internal error details for server logs only")


if __name__ == "__main__":
    app.run(debug=True)
