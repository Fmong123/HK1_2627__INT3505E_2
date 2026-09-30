from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException

app = Flask(__name__)
app.json.compact = False  # Xuống dòng và thụt lề JSON cho dễ đọc.


class ProblemError(Exception):
    def __init__(self, status, title, detail):
        super().__init__(detail)
        self.status, self.title, self.detail = status, title, detail


def problem_response(status, title, detail, response=None):
    headers = response.headers.copy() if response is not None else {}
    headers.pop("Content-Length", None)
    headers["Content-Type"] = "application/problem+json"
    return jsonify({
        "type": "about:blank",
        "title": title,
        "detail": detail,
        "status": status,
        "instance": request.path,
    }), status, headers


@app.errorhandler(ProblemError)
def handle_problem(error):
    return problem_response(error.status, error.title, error.detail)


@app.errorhandler(HTTPException)
def handle_http(error):
    # Giữ các HTTP header cần thiết, ví dụ Allow khi trả 405.
    return problem_response(
        error.code, error.name, error.description, error.get_response()
    )


@app.errorhandler(Exception)
def handle_unexpected(error):
    app.logger.exception("Unhandled exception")
    return problem_response(
        500, "Internal Server Error", "An unexpected error occurred."
    )


@app.get("/resources/<int:resource_id>")
def get_resource(resource_id):
    raise ProblemError(404, "Not Found", f"Resource {resource_id} not found.")


@app.get("/crash")
def crash():
    # Route minh họa lỗi chưa được bắt.
    raise RuntimeError("Internal error details for server logs only")


if __name__ == "__main__":
    app.run(debug=False)
