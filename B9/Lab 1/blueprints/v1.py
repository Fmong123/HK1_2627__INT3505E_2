from flask import Blueprint, current_app

from .users_data import get_user

bp = Blueprint("v1", __name__, url_prefix="/users")


@bp.after_request
def add_sunset_header(response):
    sunset = current_app.config.get("V1_SUNSET")
    if sunset:
        response.headers["Sunset"] = sunset
    return response


@bp.get("/<int:uid>")
def get(uid):
    user = get_user(uid)
    if user is None:
        return {"error": "nf"}, 404
    return {
        "id": uid,
        "full_name": f"{user['first_name']} {user['last_name']}",
        "email": user["email"],
    }
