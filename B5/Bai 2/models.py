from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

book_authors = db.Table(
    "book_authors",
    db.Column("book_id", db.Integer, db.ForeignKey("books.id"), primary_key=True),
    db.Column("author_id", db.Integer, db.ForeignKey("authors.id"), primary_key=True),
)


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(50), unique=True, nullable=False)


class Author(db.Model):
    __tablename__ = "authors"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    bio = db.Column(db.Text, default="")
    books = db.relationship("Book", secondary=book_authors, back_populates="authors")


class Book(db.Model):
    __tablename__ = "books"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    isbn = db.Column(db.String(13), unique=True, nullable=False)
    price_vnd = db.Column(db.Integer, nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=0)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)

    category = db.relationship("Category", lazy="joined")
    authors = db.relationship(
        "Author", secondary=book_authors, back_populates="books", lazy="selectin"
    )

    def to_dict(self):
        return {
            "id": f"book_{self.id}",
            "title": self.title,
            "isbn": self.isbn,
            "price": self.price_vnd,
            "stock": self.stock,
            "genre": self.category.slug,
            "authors": [{"id": a.id, "name": a.name} for a in self.authors],
        }


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    display_name = db.Column(db.String(100), nullable=False)


class Review(db.Model):
    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey("books.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    book = db.relationship("Book", backref="reviews")
    user = db.relationship("User", backref="reviews")
    __table_args__ = (db.CheckConstraint("rating BETWEEN 1 AND 5"),)
