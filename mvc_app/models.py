# models.py — MODEL (MVC)
#
# This is the Model layer. It defines what our database tables look like
# and provides helper methods to work with the data.
#
# We use SQLAlchemy — a library that lets us work with the database
# using Python classes instead of writing raw SQL queries.
# Each class below represents one table in the database.

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# This object connects our Python code to the database.
# We set it up here and connect it to the Flask app in app.py.
db = SQLAlchemy()


class User(UserMixin, db.Model):
    """
    Represents a registered user.

    Columns:
      id            — unique number for each user (auto-generated)
      username      — the name they log in with (must be unique)
      password_hash — their password, stored in a scrambled form
      email         — their email address (must be unique)
      role          — either 'user' or 'admin'
      created_at    — when the account was created
    """

    __tablename__ = "users"

    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(50), nullable=False, unique=True)
    password_hash = db.Column(db.String(256), nullable=False)
    email         = db.Column(db.String(120), nullable=False, unique=True)
    role          = db.Column(db.String(20), nullable=False, default="user")
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    # A user can have many posts (one-to-many relationship)
    posts = db.relationship("Post", back_populates="author", lazy=True)

    def set_password(self, plaintext):
        """Scramble the password before storing it in the database."""
        self.password_hash = generate_password_hash(plaintext)

    def check_password(self, plaintext):
        """Check if a given password matches the stored scrambled version."""
        return check_password_hash(self.password_hash, plaintext)

    @property
    def is_admin(self):
        """Returns True if this user has the admin role."""
        return self.role == "admin"

    def __repr__(self):
        return f"<User id={self.id} username={self.username!r} role={self.role!r}>"


class Post(db.Model):
    """
    A simple blog post written by a user.
    Each post belongs to one user (the author).
    One user can have many posts — this is called a one-to-many relationship.
    """

    __tablename__ = "posts"

    id         = db.Column(db.Integer, primary_key=True)
    title      = db.Column(db.String(120), nullable=False)
    content    = db.Column(db.Text, nullable=False)
    author_id  = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Link back to the User who wrote this post
    author = db.relationship("User", back_populates="posts")

    def __repr__(self):
        return f"<Post id={self.id} title={self.title!r} author_id={self.author_id}>"
