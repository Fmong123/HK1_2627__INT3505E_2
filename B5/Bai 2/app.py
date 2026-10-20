from flask import Flask

from models import db
from routes.books import bp

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///books.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.ensure_ascii = False

db.init_app(app)
app.register_blueprint(bp)

with app.app_context():
    db.create_all()  

if __name__ == "__main__":
    app.run(debug=True)
