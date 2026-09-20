import hashlib
import json
from flask import Flask, jsonify, request, make_response

app = Flask(__name__)
BOOKS = {
    1: {"id": 1, "title": "Clean Code", "author": "Robert C. Martin", "price": 35.0},
    2: {"id": 2, "title": "Clean Architecture", "author": "Robert C. Martin", "price": 40.0}
}

@app.get("/books/<int:book_id>")
def get_book(book_id):
    book = BOOKS.get(book_id)
    if not book:
        return jsonify(error="Book not found"), 404

    body_bytes = json.dumps(book, sort_keys=True).encode("utf-8")
    etag = f'"{hashlib.md5(body_bytes).hexdigest()}"'

    client_etag = request.headers.get("If-None-Match")

    if client_etag == etag:
        response = make_response("", 304)
        response.headers["ETag"] = etag
        return response
    
    response = make_response(jsonify(book), 200)
    response.headers["ETag"] = etag
    return response

if __name__ == "__main__":
    app.run(debug=True)