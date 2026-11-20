"""Demo order handlers; orders are not persisted."""

from uuid import uuid4


def v1_create_order(body):
    return {
        "order_id": str(uuid4()),
        "account_id": body["account_id"],
        "version": "v1",
    }


def v2_create_order(body):
    return {
        "order_id": str(uuid4()),
        "account_id": body["account_id"],
        "version": "v2",
        "status": "created",
    }
