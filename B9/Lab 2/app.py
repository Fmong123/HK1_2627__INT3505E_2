"""Practice 2: select the User API version through a request header."""

from functools import wraps

from flask import Flask, jsonify, make_response, request

LATEST = "2"
SUPPORTED = frozenset({"1", "2", "2024-06-20"})
USERS = {1: {"f": "Văn", "l": "Nguyễn", "e": "a@vnu.vn"}}


def api_version(supported=SUPPORTED, default=LATEST):
    """Validate the requested version and report the version actually served."""
    if default not in supported:
        raise ValueError("The default version must be supported")

    def decorate(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            version = request.headers.get("X-API-Version", default)
            if version not in supported:
                return jsonify(error="unsupported version"), 400

            response = make_response(fn(version, *args, **kwargs))
            response.headers["X-API-Version-Served"] = version
            response.vary.add("X-API-Version")
            return response

        return wrapper

    return decorate


app = Flask(__name__)
app.json.ensure_ascii = False


@app.get("/users/<int:uid>")
@api_version()
def get_user(version, uid):
    user = USERS.get(uid)
    if user is None:
        return {"error": "not found"}, 404
    if version == "1":
        return {"id": uid, "full_name": f"{user['f']} {user['l']}"}
    return {
        "id": uid,
        "first_name": user["f"],
        "last_name": user["l"],
        "email": user["e"],
    }


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
