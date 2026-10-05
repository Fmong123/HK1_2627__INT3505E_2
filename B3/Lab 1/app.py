from flask import Flask, jsonify, request

app = Flask(__name__)

POSTS = [
    {
        "id": 1,
        "title": "Bai viet dau tien",
        "content": "Noi dung bai 1",
        "author_id": 101,
    },
    {
        "id": 2,
        "title": "Hoc Flask API",
        "content": "Noi dung bai 2",
        "author_id": 102,
    },
]
_next_id = 3

def find_post(post_id):
    return next((p for p in POSTS if p["id"] == post_id), None)

@app.route("/v1/posts", methods=["GET"])
def list_posts():
    return jsonify({"data": POSTS, "total": len(POSTS)}), 200

@app.route("/v1/posts/<int:post_id>", methods=["GET"])
def get_post(post_id):
    post = find_post(post_id)
    if post is None:
        return jsonify({"error": "Post not found"}), 404
    return jsonify(post), 200

@app.route("/v1/posts", methods=["POST"])
def create_post():
    global _next_id
    if not request.is_json:
        return jsonify({"error": "Expected JSON"}), 415
    
    data = request.get_json(silent=True) or {}
    if data is None:
        return jsonify({"error": "Invalid or malformed JSON format"}), 400
    
    title = data.get("title").strip()
    content = data.get("content").strip()
    author_id = data.get("author_id") or 1
    if not title or not content is None:
        return jsonify({"error": "Title and content are required"}), 422
    
    post = {"id": _next_id, "title": title, "content": content, "author_id": author_id}
    POSTS.append(post)
    _next_id += 1
    return jsonify(post), 201

@app.route("/v1/posts/<int:post_id>", methods=["PUT"])
def update_post(post_id):
    post = find_post(post_id)
    if not post:
        return jsonify({"error": "Post not found"}), 404

    body = request.get_json(silent=True) or {}
    post["title"] = body.get("title", post["title"])
    post["content"] = body.get("content", post["content"])

    return jsonify(post), 200

@app.route("/v1/posts/<int:post_id>", methods=["DELETE"])
def delete_post(post_id):
    post = find_post(post_id)
    if not post:
        return jsonify({"error": "Post not found"}), 404

    POSTS.remove(post)
    return "", 204

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)