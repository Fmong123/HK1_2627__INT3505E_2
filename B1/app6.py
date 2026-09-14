from flask import Flask, jsonify, request
app = Flask(__name__)

BOOKS = [
    {"id":1,"title":"Clean Code","author":"R. Martin"},
    {"id":2,"title":"KTHDV","author":"NQPhong"},
    {"id":3,"title":"How To Basic","author":"hehe"}
    ]

_next = 4
def find(bid):
    return next((b for b in BOOKS if b["id"] == bid), None)

# LIST — GET /books
@app.route("/books", methods=["GET"])
def list_books():
    n = int(request.args.get("limit", 100))
    q = request.args.get("q", "").strip().lower()
    sort_by = request.args.get("sort", "").strip().lower()

    items = list(BOOKS)
    if q:
        items = [b for b in items if q in b["title"].lower() 
                or q in b["author"].lower()]
    if sort_by == "title":
        items.sort(key=lambda b: b["title"].lower())
    elif sort_by == "-title":
        items.sort(key=lambda b: b["title"].lower(), reverse=True)
    elif sort_by == "year":
        items.sort(key=lambda b: b["year"])

    return jsonify(items[:n]), 200
# DETAIL — GET /books/<int:id>
@app.route("/books/<int:bid>", methods=["GET"])
def get_book(bid):
    book = find(bid)
    if not book: 
        return {"error":"not found"}, 404
    return jsonify(book), 200
# CREATE — POST /books
@app.route("/books", methods=["POST"])
def create_book():
    global _next
    body = request.get_json(silent=True) or {}
    t, a, y = body.get("title"), body.get("author"), body.get("year")
    if not t or not a:
        return {"error":"need title+author"}, 400
    if y is None or not isinstance(y, int) or y < 1900:
        return {"error":"need year >= 1900"}, 400
    book = {"id": _next, "title": t, "author": a, "year": y}
    _next += 1
    BOOKS.append(book)
    return jsonify(book), 201, {"Location": f"/books/{book['id']}"}
# MODIFY
@app.route("/books/<int:bid>", methods=["PUT", "DELETE"])
def modify_book(bid):
    book = find(bid)
    if not book: 
        return {"error":"not found"}, 404
    if request.method == "PUT":
        body = request.get_json(silent=True) or {}
        y = body.get("year")
        if y is not None and (not isinstance(y, int) or y < 1900):
            return {"error":"need year >= 1900"}, 400
        book.update(body)
        return jsonify(book), 200
    BOOKS.remove(book)
    return "", 204

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)