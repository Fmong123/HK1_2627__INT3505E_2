"""Practice 4: blue-green routing through one POST /orders endpoint."""

from flask import Flask, jsonify, request

from gateway import dispatch

app = Flask(__name__)
app.json.ensure_ascii = False


@app.route("/orders", methods=["POST"])
def create_order():
    body = request.get_json()
    if (
        not isinstance(body, dict)
        or not isinstance(body.get("account_id"), str)
        or not body["account_id"].strip()
    ):
        return jsonify(error="account_id must be a non-empty string"), 400

    which, result = dispatch(body)
    resp = jsonify(result)
    resp.headers["X-Order-Handler"] = which
    return resp, (201 if which == "v2" else 200)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
