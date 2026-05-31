# models.py
# CSA Session 43 — Web Development Foundations
#
# This file is the MODEL layer of the MVC pattern.
# It defines the database schema using SQLAlchemy and provides
# helper methods for password hashing and role checking.
#
# The Controller (app.py) never writes raw SQL.
# It creates and queries Model objects — SQLAlchemy translates
# those into safe parameterised SQL queries automatically.

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """
    Represents a registered user.

    SCHEMA NOTES:
      id            — surrogate primary key, auto-incremented
      username      — unique login name
      password_hash — hashed password; plaintext is never stored
      email         — unique, used for account identification
      role          — 'user' or 'admin'; defaults to 'user'
      created_at    — timestamp of account creation
    """

    __tablename__ = "users"

    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(50), nullable=False, unique=True)
    password_hash = db.Column(db.String(256), nullable=False)
    email         = db.Column(db.String(120), nullable=False, unique=True)
    role          = db.Column(db.String(20), nullable=False, default="user")
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    posts = db.relationship("Post", back_populates="author", lazy=True)

    def set_password(self, plaintext: str) -> None:
        """Hash the password with PBKDF2-SHA256 before storing."""
        self.password_hash = generate_password_hash(plaintext)

    def check_password(self, plaintext: str) -> bool:
        """Verify a plaintext password against the stored hash."""
        return check_password_hash(self.password_hash, plaintext)

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"

    def __repr__(self):
        return f"<User id={self.id} username={self.username!r} role={self.role!r}>"


class Post(db.Model):
    """
    A simple user-authored post.
    Demonstrates a one-to-many relationship: one User → many Posts.
    """

    __tablename__ = "posts"

    id         = db.Column(db.Integer, primary_key=True)
    title      = db.Column(db.String(120), nullable=False)
    content    = db.Column(db.Text, nullable=False)
    author_id  = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    author = db.relationship("User", back_populates="posts")

    def __repr__(self):
        return f"<Post id={self.id} title={self.title!r} author_id={self.author_id}>"
