# minimal_app.py
# The most basic Flask web app with user accounts.
#
# Features: register, login, personalised welcome page.
#
# Why raw sqlite3 and not SQLAlchemy?
# SQLAlchemy is a library (ORM) that sits on top of sqlite3 and adds a lot of
# structure — models, sessions, migrations. It is the right choice for a
# real-world app. Here we use Python's built-in sqlite3 directly so you can
# see exactly what is happening at the database level without any abstraction
# in the way. Every query you see here is real SQL, nothing hidden.
#
# Why SQLite and not MySQL or PostgreSQL?
# SQLite stores the entire database in a single file (minimal.db) on your disk.
# No server to install, no configuration needed. Perfect for learning and for
# small apps. Real production apps use MySQL or PostgreSQL for scale.
#
# Run:  python minimal_app.py
# Open: http://localhost:5002

from flask import Flask, request, redirect, session
import sqlite3

app = Flask(__name__)

# secret_key is used by Flask to sign the session cookie.
# In a real app this must be a long random string kept secret.
app.secret_key = "change-this-in-a-real-app"

DB = "minimal.db"

# ── Database setup ────────────────────────────────────────────────────────────
# This runs once when the app starts.
# CREATE TABLE IF NOT EXISTS means it will not fail if the table already exists.

with sqlite3.connect(DB) as db:
    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT    NOT NULL UNIQUE,
            password TEXT    NOT NULL
        )
    """)

# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    # Send logged-in users to dashboard, everyone else to login.
    if session.get("username"):
        return redirect("/dashboard")
    return redirect("/login")


@app.route("/register", methods=["GET", "POST"])
def register():
    error = ""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        try:
            with sqlite3.connect(DB) as db:
                db.execute(
                    "INSERT INTO users (username, password) VALUES (?, ?)",
                    (username, password)
                )
            # Registration successful — send them to login
            return redirect("/login")
        except sqlite3.IntegrityError:
            # UNIQUE constraint on username failed — someone already has that name
            error = "That username is already taken. Please choose another."

    return f"""
        <h2>Register</h2>
        <p style='color:red'>{error}</p>
        <form method='post'>
            Username: <input name='username'><br><br>
            Password: <input name='password' type='password'><br><br>
            <button type='submit'>Register</button>
        </form>
        <a href='/login'>Already have an account? Login</a>
    """


@app.route("/login", methods=["GET", "POST"])
def login():
    error = ""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        with sqlite3.connect(DB) as db:
            row = db.execute(
                "SELECT * FROM users WHERE username = ? AND password = ?",
                (username, password)
            ).fetchone()
        if row:
            # Store the username in the session so we remember who is logged in
            session["username"] = username
            return redirect("/dashboard")
        error = "Wrong username or password."

    return f"""
        <h2>Login</h2>
        <p style='color:red'>{error}</p>
        <form method='post'>
            Username: <input name='username'><br><br>
            Password: <input name='password' type='password'><br><br>
            <button type='submit'>Login</button>
        </form>
        <a href='/register'>No account? Register here</a>
    """


@app.route("/dashboard")
def dashboard():
    # If someone tries to visit this page without logging in, send them away.
    if not session.get("username"):
        return redirect("/login")
    return f"""
        <h2>Hi {session['username']}!</h2>
        <p>You are logged in.</p>
        <a href='/logout'>Logout</a>
    """


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True, port=5002)
