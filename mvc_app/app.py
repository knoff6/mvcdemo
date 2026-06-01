# app.py — CONTROLLER (MVC)
#
# This is the Controller layer. It handles incoming web requests:
#   1. Receives the request (e.g. someone visits /login)
#   2. Talks to the Model (database) to get or save data
#   3. Passes data to the View (HTML template) to display
#
# Run:
#   pip install -r requirements.txt
#   flask run --debug

import re

from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, abort
)
from flask_login import (
    LoginManager, login_user, logout_user,
    login_required, current_user
)

from config import Config
from models import db, User, Post

# ── Create the Flask app ─────────────────────────────────────────────────────

app = Flask(__name__)
app.config.from_object(Config)

# Connect SQLAlchemy (our database library) to the Flask app
db.init_app(app)

# Set up Flask-Login (a library that manages user sessions for us)
login_manager = LoginManager(app)
login_manager.login_view = "login"              # Where to send users who aren't logged in
login_manager.login_message_category = "info"    # Style of the "please log in" message

# ── User loader ──────────────────────────────────────────────────────────────
# Flask-Login calls this function to find out who is logged in.
# It receives the user's ID (stored in their session cookie) and
# returns the matching User object from the database.

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# ── Seed the database ────────────────────────────────────────────────────────
# This runs once on first startup to create tables and add sample users
# so you have accounts to test with right away.

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
            title="Welcome to the Lab",
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
#  ROUTES
#  Each @app.route maps a URL to a Python function.
#  The function does its work and returns HTML for the browser to display.
# ══════════════════════════════════════════════════════════════════════════════

# ── Home page ─────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    # Logged-in users go to the dashboard, everyone else goes to login.
    return redirect(url_for("dashboard" if current_user.is_authenticated else "login"))


# ── Registration ──────────────────────────────────────────────────────────────

@app.route("/register", methods=["GET", "POST"])
def register():
    """GET = show the form. POST = process the form and create an account."""
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        # Read what the user typed into the form
        username = request.form.get("username", "")
        email    = request.form.get("email", "")
        password = request.form.get("password", "")

        # Check for problems with the input
        errors = []
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

        # If there are errors, show them and let the user try again
        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("register.html")

        # Everything looks good — create the new user and save to database
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
    """GET = show the form. POST = check credentials and log the user in."""
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        # Look up the user in the database and check their password
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user, remember=False)
            return redirect(url_for("dashboard"))

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
    """Show all posts. Only logged-in users can see this page."""
    # Get all posts from the database, newest first
    posts = Post.query.order_by(Post.created_at.desc()).all()
    # Pass the data to the template (View) for display
    return render_template("dashboard.html", user=current_user, posts=posts)


# ── Post detail ───────────────────────────────────────────────────────────────

@app.route("/post/<int:post_id>")
@login_required
def view_post(post_id):
    """Show a single post. Returns a 404 error if the post doesn't exist."""
    post = db.session.get(Post, post_id) or abort(404)
    return render_template("post.html", post=post)


# ── Admin panel ───────────────────────────────────────────────────────────────

@app.route("/admin")
@login_required
def admin_panel():
    """Only admin users can access this page."""
    if not current_user.is_admin:
        abort(403)
    users = User.query.all()
    return render_template("admin.html", users=users)


# ── Search ────────────────────────────────────────────────────────────────────

@app.route("/search")
@login_required
def search():
    """Search for posts by title."""
    query = request.args.get("q", "")
    results = []
    if query:
        # Find posts whose title contains the search term (case-insensitive)
        results = Post.query.filter(Post.title.ilike(f"%{query}%")).all()
    return render_template("search.html", query=query, results=results)


# ── Entry point ───────────────────────────────────────────────────────────────
# This block runs when you execute: python app.py
# It creates the database tables and starts the web server.

if __name__ == "__main__":
    with app.app_context():
        seed_database()
    app.run(debug=True, host="0.0.0.0", port=5000)
