# app.py
# CSA Session 43 — Web Development Foundations
#
# This file is the CONTROLLER layer of the MVC pattern.
# Route functions receive HTTP requests, interact with the Model,
# and pass data to the View (Jinja2 templates).
#
# Run:
#   pip install -r requirements.txt
#   flask run --debug

import re
import os

from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash, abort
)
from flask_login import (
    LoginManager, login_user, logout_user,
    login_required, current_user
)

from config import Config
from models import db, User, Post

# ── App factory ───────────────────────────────────────────────────────────────

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"

# ── Flask-Login user loader ───────────────────────────────────────────────────

@login_manager.user_loader
def load_user(user_id: str):
    return db.session.get(User, int(user_id))


# ── Database initialisation ───────────────────────────────────────────────────

def seed_database():
    """Create tables and insert sample data if the DB is empty."""
    db.create_all()
    if User.query.count() == 0:
        admin = User(username="admin", email="admin@lab.local", role="admin")
        admin.set_password("Admin1234!")

        alice = User(username="alice", email="alice@lab.local")
        alice.set_password("AlicePass1!")

        bob = User(username="bob", email="bob@lab.local")
        bob.set_password("BobPass1!")

        db.session.add_all([admin, alice, bob])
        db.session.flush()

        p1 = Post(
            title="Welcome to the CSA Lab",
            content="This is a sample post created by the admin.",
            author_id=admin.id
        )
        p2 = Post(
            title="Alice's First Post",
            content="Hello from Alice!",
            author_id=alice.id
        )
        db.session.add_all([p1, p2])
        db.session.commit()
        print("[seed] Database seeded with admin / alice / bob users.")


# ══════════════════════════════════════════════════════════════════════════════
# ROUTES — CONTROLLER LAYER
# Each function below maps a URL to a Python function via @app.route.
# The function reads input, talks to the Model, and returns a View.
# ══════════════════════════════════════════════════════════════════════════════

# ── Home ──────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return redirect(url_for("dashboard" if current_user.is_authenticated else "login"))


# ── Registration ──────────────────────────────────────────────────────────────

@app.route("/register", methods=["GET", "POST"])
def register():
    """
    GET  → show the registration form (View)
    POST → read form input, validate, create User in DB, redirect to login
    """
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "")
        email    = request.form.get("email", "")
        password = request.form.get("password", "")

        errors = []

        # Input validation — length and format
        if len(username) < 3 or len(username) > 50:
            errors.append("Username must be 3–50 characters.")
        if not re.match(r"^[a-zA-Z0-9_]+$", username):
            errors.append("Username may only contain letters, digits, and underscores.")
        if len(password) < 8:
            errors.append("Password must be at least 8 characters.")
        if not re.search(r"[A-Z]", password):
            errors.append("Password must contain at least one uppercase letter.")
        if not re.search(r"[0-9]", password):
            errors.append("Password must contain at least one digit.")
        if User.query.filter_by(username=username).first():
            errors.append("Username already taken.")
        if User.query.filter_by(email=email).first():
            errors.append("Email already registered.")

        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("register.html")

        # Create the User Model object and save to DB
        user = User(username=username, email=email, role="user")
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash("Account created. Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


# ── Login ─────────────────────────────────────────────────────────────────────

@app.route("/login", methods=["GET", "POST"])
def login():
    """
    GET  → show the login form
    POST → check credentials via Model, start session, redirect to dashboard
    """
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user, remember=False)
            next_page = request.args.get("next")
            if next_page and not next_page.startswith("/"):
                next_page = None
            return redirect(next_page or url_for("dashboard"))

        flash("Invalid username or password.", "danger")

    return render_template("login.html")


# ── Logout ────────────────────────────────────────────────────────────────────

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


# ── Dashboard ─────────────────────────────────────────────────────────────────

@app.route("/dashboard")
@login_required
def dashboard():
    """
    Protected page — @login_required redirects to /login if not authenticated.
    Passes all posts to the View (dashboard.html) for rendering.
    """
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template("dashboard.html", user=current_user, posts=posts)


# ── Post detail ───────────────────────────────────────────────────────────────

@app.route("/post/<int:post_id>")
@login_required
def view_post(post_id: int):
    post = db.session.get(Post, post_id) or abort(404)
    return render_template("post.html", post=post)


# ── Admin panel ───────────────────────────────────────────────────────────────

@app.route("/admin")
@login_required
def admin_panel():
    """Only users with role=admin can access this page."""
    if not current_user.is_admin:
        abort(403)
    users = User.query.all()
    return render_template("admin.html", users=users)


# ── Search ────────────────────────────────────────────────────────────────────

@app.route("/search")
@login_required
def search():
    """Search post titles. Results passed to the View for rendering."""
    query = request.args.get("q", "")
    results = []
    if query:
        results = Post.query.filter(Post.title.ilike(f"%{query}%")).all()
    return render_template("search.html", query=query, results=results)


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    with app.app_context():
        seed_database()
    app.run(debug=True, host="0.0.0.0", port=5000)
