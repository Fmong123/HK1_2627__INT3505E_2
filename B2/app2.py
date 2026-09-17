from flask import Flask, jsonify, make_response, request
app = Flask(__name__)
BOOKS = [
    {"id": 1, "title": "Clean Code", "author": "R. Martin", "isbn": "9780132350884", "price": 29.99},
    {"id": 2, "title": "DDIA", "author": "Kleppmann", "isbn": "9781449373320", "price": 45.00},
    {"id": 3, "title": "Hehehe", "author": "Phong", "isbn": "120720061595", "price": 67.00}
]
_next_id = 4

@app.get("/books/<int:bid>")
def fetch(bid):
    i = next((k for k, b in enumerate(BOOKS) if b["id"] == bid), None)
    if i is None:
        return jsonify(error="not found"), 404
    
    resp = make_response(jsonify(BOOKS[i]), 200)
    resp.headers["Cache-Control"] = "max-age=60"
    return resp

@app.put("/books/<int:bid>")
def put(bid):
    i = next((k for k, b in enumerate(BOOKS) if b["id"] == bid), None)
    if i is None:
        return jsonify(error="not found"), 404
    
    p = request.get_json(silent=True) or {}
    t, a, isbn, price = p.get("title", "").strip(), p.get("author", "").strip(), p.get("isbn"), p.get("price")
    if not t or not a:
        return jsonify(error="need title+author"), 422
    
    BOOKS[i] = {
        "id": bid,
        "title": t,
        "author": a,
        "isbn": isbn,
        "price": price
    }
    return jsonify(BOOKS[i]), 200   

@app.patch("/books/<int:bid>")
def patch(bid):
    i = next((k for k, b in enumerate(BOOKS) if b["id"] == bid), None)
    if i is None:
        return jsonify(error="not found"), 404
    
    p = request.get_json(silent=True) or {}
    if p.get("price", 0) < 0:
        return jsonify(error="price must be positive"), 422

    for k in "title author isbn price".split():
        if k in p:
            BOOKS[i][k] = p[k]
            
    return jsonify(BOOKS[i]), 200

@app.delete("/books/<int:bid>")
def delete(bid):
    i = next((k for k, b in enumerate(BOOKS) if b["id"] == bid), None)
    if i is None:
        return jsonify(error="not found"), 404
    
    BOOKS.pop(i)
    return "", 204

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)