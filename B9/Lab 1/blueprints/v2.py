from flask import Blueprint, request, url_for

from .users_data import create_user, get_user

bp = Blueprint("v2", __name__, url_prefix="/users")


@bp.get("/<int:uid>")
def get(uid):
    user = get_user(uid)
    if user is None:
        return {"error": "nf"}, 404
    return {"id": uid, **user}


@bp.post("")
def create():
    if not request.is_json:
        return {"error": "Content-Type must be application/json"}, 415
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return {"error": "Request body must be a valid JSON object"}, 400

    fields = {"first_name", "last_name", "email"}
    if set(data) != fields:
        return {"error": "Provide exactly first_name, last_name and email"}, 400
    if any(not isinstance(data[key], str) or not data[key].strip() for key in fields):
        return {"error": "first_name, last_name and email must be non-empty strings"}, 400

    cleaned = {key: data[key].strip() for key in fields}
    email = cleaned["email"]
    if email.count("@") != 1 or any(char.isspace() for char in email):
        return {"error": "Invalid email"}, 400
    local, domain = email.split("@")
    if not local or not domain:
        return {"error": "Invalid email"}, 400

    uid, user = create_user(**cleaned)
    return {"id": uid, **user}, 201, {"Location": url_for("v2.get", uid=uid)}
