"""Shared in-memory data for both API versions (reset on restart)."""

from threading import Lock

USERS = {
    1: {"first_name": "Văn", "last_name": "Nguyễn", "email": "a@vnu.vn"},
    2: {"first_name": "Trang", "last_name": "Trần", "email": "b@vnu.vn"},
}
_lock = Lock()


def get_user(uid):
    return USERS.get(uid)


def create_user(first_name, last_name, email):
    with _lock:
        uid = max(USERS, default=0) + 1
        user = {"first_name": first_name, "last_name": last_name, "email": email}
        USERS[uid] = user
    return uid, user
