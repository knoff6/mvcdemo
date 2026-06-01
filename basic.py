# basic.py
# A single-file Flask web app with user accounts.
# Features: register, login, and a personalised welcome page.
#
# This is the simplest possible version — everything lives in one file
# so you can read it top to bottom and understand the whole app.
#
# We use Python's built-in sqlite3 module (no extra install) so you can
# see the actual SQL queries. The database is just a file called minimal.db.
#
# Run:  python basic.py
# Open: http://localhost:5002

from flask import Flask, request, redirect, session
import sqlite3

app = Flask(__name__)

# Flask uses this key to keep track of who is logged in (via cookies).
app.secret_key = "change-this-in-a-real-app"

# Name of the database file. SQLite stores everything in this one file.
DB = "minimal.db"

# ── Database setup ────────────────────────────────────────────────────────────
# This runs once when the app starts.
# It creates a "users" table if one doesn't already exist.
# Each user has an id, a username, and a password.

with sqlite3.connect(DB) as db:
    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT    NOT NULL UNIQUE,
            password TEXT    NOT NULL
        )
    """)

# ── Routes ────────────────────────────────────────────────────────────────────
# Each @app.route tells Flask: "when someone visits this URL, run this function."

@app.route("/")
def index():
    # If the user is logged in, go to the dashboard. Otherwise, go to login.
    if session.get("username"):
        return redirect("/dashboard")
    return redirect("/login")


@app.route("/register", methods=["GET", "POST"])
def register():
    # GET  = show the registration form
    # POST = the form was submitted, so create the account
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
            # Account created — send them to the login page
            return redirect("/login")
        except sqlite3.IntegrityError:
            # The username already exists in the database
            error = "That username is already taken. Please choose another."

    # Return a simple HTML page with the registration form.
    # This is inline HTML — no separate template file needed.
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
    # GET  = show the login form
    # POST = the form was submitted, so check the credentials
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
            # Credentials are correct — remember who is logged in
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
    # Only logged-in users can see this page.
    if not session.get("username"):
        return redirect("/login")
    return f"""
        <h2>Hi {session['username']}!</h2>
        <p>You are logged in.</p>
        <a href='/logout'>Logout</a>
    """


@app.route("/logout")
def logout():
    # Clear the session so the user is no longer logged in.
    session.clear()
    return redirect("/login")


# ── Entry point ───────────────────────────────────────────────────────────────
# This block runs when you execute: python basic.py
# debug=True means Flask will auto-reload when you change the code.

if __name__ == "__main__":
    app.run(debug=True, port=5002)
