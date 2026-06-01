# Security Considerations

This document covers the security aspects of both apps in this repository. The source code itself is kept simple and beginner-friendly — all security discussion lives here.

---

## How to Read This Document

Each section covers a feature area (registration, login, etc.) and explains:
- What the app does now
- What could go wrong (attack surface)
- What a production app should do instead (best practice)

---

## 1. Password Storage

### Basic App (`basic.py`)

**What it does:** Stores passwords in **plaintext** — exactly as the user typed them.

**Attack surface:** Anyone who can read the database file (`minimal.db`) can see every user's password. This includes:
- A developer or sysadmin with file access
- An attacker who exploits a separate vulnerability (e.g. directory traversal) to download the database
- Database backups stored insecurely

**Best practice:** Never store plaintext passwords. Use a one-way hashing algorithm (bcrypt, scrypt, or PBKDF2) so that even if the database is stolen, the original passwords cannot be recovered.

### MVC App (`mvc_app`)

**What it does:** Hashes passwords using **PBKDF2-SHA256** (via Werkzeug's `generate_password_hash`). The original password is never stored.

**Why this is better:** Even with full database access, an attacker only sees hashed values. Reversing a PBKDF2 hash is computationally expensive and impractical for strong passwords.

**Could be even better:** Use **bcrypt** or **argon2** — they are specifically designed for password hashing and are more resistant to GPU-based brute-force attacks than PBKDF2.

---

## 2. Session Management

### Basic App

**What it does:** Uses Flask's built-in `session` object with a hardcoded `secret_key = "change-this-in-a-real-app"`.

**Attack surface:**
- The secret key is visible in the source code. Anyone who knows it can forge session cookies and impersonate any user.
- The key is short and predictable.

**Best practice:**
- Generate a long, random secret key (e.g. `python -c "import secrets; print(secrets.token_hex(32))"`)
- Store it in an environment variable, never in source code
- Rotate it periodically

### MVC App

**What it does:** Reads the secret key from an environment variable, falling back to a default for development.

**Attack surface:** The development default (`csa-lab-dev-key-change-in-prod`) is still in the source code. If deployed to production without setting the environment variable, it is just as vulnerable as the basic app.

**Best practice:** Fail loudly in production if `SECRET_KEY` is not set (raise an error on startup instead of using a fallback).

---

## 3. Input Validation

### Basic App

**What it does:** No input validation at all. Empty usernames, empty passwords, or extremely long strings are all accepted.

**Attack surface:**
- Users can register with blank credentials
- No length limits — could be used for denial-of-service by submitting enormous payloads
- No character restrictions — special characters in usernames could cause issues in other parts of the app

### MVC App

**What it does:** Server-side validation in `app.py`:
- Username must be 3–50 characters, letters/digits/underscores only
- Password must be 8+ characters with at least one uppercase letter and one digit
- Duplicate usernames and emails are rejected

**Attack surface:**
- Client-side validation (HTML `pattern`, `minlength`, `maxlength` attributes) can be bypassed by modifying the HTTP request directly (e.g. using browser DevTools or an intercepting proxy)
- Server-side validation catches this, but only if it mirrors all client-side checks

**Best practice:** Always validate on the server. Client-side validation is a convenience for the user, not a security measure.

---

## 4. SQL Injection

### Basic App

**What it does:** Uses **parameterised queries** (`?` placeholders) for all SQL operations.

```python
db.execute(
    "SELECT * FROM users WHERE username = ? AND password = ?",
    (username, password)
)
```

**Why this matters:** The `?` placeholders tell SQLite to treat the values as data, not as SQL code. This prevents SQL injection — an attack where a malicious user crafts input that changes the meaning of the SQL query.

**Example of what would be vulnerable:**
```python
# NEVER DO THIS — string concatenation in SQL
db.execute(f"SELECT * FROM users WHERE username = '{username}'")
```
An attacker could enter `' OR 1=1 --` as the username to bypass authentication.

### MVC App

**What it does:** Uses **SQLAlchemy ORM**, which generates parameterised queries automatically. The developer never writes raw SQL.

**Attack surface:** The search feature uses `ilike(f"%{query}%")` — while SQLAlchemy parameterises this safely, the pattern itself could be abused with SQL wildcard characters (`%`, `_`) to extract information about post titles.

---

## 5. Cross-Site Request Forgery (CSRF)

### Both Apps

**What they do:** Neither app includes CSRF protection.

**Attack surface:** An attacker could create a malicious webpage that submits a form to the app on behalf of a logged-in user. For example, a hidden form that POSTs to `/register` or triggers `/logout`.

**Best practice:** Use CSRF tokens — a random value embedded in each form that the server verifies on submission. Flask-WTF provides this out of the box.

---

## 6. Cross-Site Scripting (XSS)

### Basic App

**What it does:** Returns HTML using f-strings:
```python
return f"<h2>Hi {session['username']}!</h2>"
```

**Attack surface:** If a username contains HTML or JavaScript (e.g. `<script>alert('XSS')</script>`), it will be rendered and executed in the browser. This is a **stored XSS** vulnerability — the malicious payload is saved in the database and served to every user who views the page.

**Best practice:** Always escape user-supplied data before inserting it into HTML. Use a templating engine (like Jinja2) that auto-escapes by default.

### MVC App

**What it does:** Uses Jinja2 templates, which auto-escape all `{{ }}` expressions by default.

**Why this is safer:** If a username contains `<script>`, Jinja2 converts it to `&lt;script&gt;` — the browser displays it as text instead of executing it.

**Remaining risk:** The `| safe` filter in Jinja2 disables escaping. If a developer adds `{{ post.content | safe }}`, any HTML in the content will be rendered. This app does not use `| safe`, but it is a common mistake to watch for.

---

## 7. Authentication & Authorisation

### Basic App

**What it does:** Manual session management. The username is stored in `session["username"]` after login and checked on each request.

**Attack surface:**
- No brute-force protection — an attacker can try unlimited username/password combinations
- No account lockout after failed attempts
- No rate limiting

### MVC App

**What it does:** Uses Flask-Login for session management. The `@login_required` decorator protects routes. Admin access is checked by `current_user.is_admin`.

**Attack surface:**
- Same brute-force concerns as the basic app — no rate limiting or lockout
- Role check is only in the Controller (`if not current_user.is_admin: abort(403)`). If a developer forgets to add this check to a new admin route, it will be accessible to everyone
- No multi-factor authentication

**Best practice:**
- Add rate limiting (e.g. Flask-Limiter)
- Lock accounts after N failed attempts
- Consider multi-factor authentication for admin accounts

---

## 8. Logout Mechanism

### Basic App

**What it does:** Logout uses a **GET request** (`@app.route("/logout")`).

**Attack surface:** Anything that causes the browser to visit `/logout` will log the user out:
- A link in an email: `<a href="http://localhost:5002/logout">Click here</a>`
- An image tag: `<img src="http://localhost:5002/logout">`
- Browser prefetching

**Best practice:** Logout should use a POST request with CSRF protection. This ensures that only the user themselves can trigger it.

### MVC App

**What it does:** Also uses GET for logout, with the same vulnerabilities.

---

## 9. Debug Mode

### Both Apps

**What they do:** Both apps run with `debug=True`.

**Attack surface:** Flask's debug mode includes an interactive debugger that lets anyone execute arbitrary Python code on the server. If the app is accessible from the network, this is a **remote code execution** vulnerability.

**Best practice:** Never enable debug mode in production. Use environment variables to control this:
```python
app.run(debug=os.environ.get("FLASK_DEBUG", "0") == "1")
```

---

## 10. Database Exposure

### Both Apps

**What they do:** Use SQLite, which stores the database as a file on disk (`minimal.db` or `csa_lab.db`).

**Attack surface:** If the web server is misconfigured, the database file could be directly downloadable via the browser (e.g. `http://localhost:5000/minimal.db`).

**Best practice:**
- Store the database file outside the web root
- Use a proper database server (PostgreSQL, MySQL) in production
- Restrict file permissions

---

## 11. HTTPS / Transport Security

### Both Apps

**What they do:** Run on plain HTTP (no encryption).

**Attack surface:** All data (including passwords and session cookies) is sent in cleartext. Anyone on the same network can intercept it (man-in-the-middle attack).

**Best practice:** Always use HTTPS in production. Obtain a TLS certificate (e.g. via Let's Encrypt) and configure the web server to enforce HTTPS.

---

## 12. Host Header / Binding

### MVC App

**What it does:** Binds to `0.0.0.0` (all network interfaces):
```python
app.run(debug=True, host="0.0.0.0", port=5000)
```

**Attack surface:** This makes the app accessible to anyone on the network, not just localhost. Combined with debug mode, this is especially dangerous.

**Best practice:** Bind to `127.0.0.1` (localhost only) during development. Use a reverse proxy (nginx, Caddy) in production.

---

## Security Comparison Summary

| Aspect | `basic.py` | `mvc_app` |
|---|---|---|
| Password storage | ❌ Plaintext | ✅ PBKDF2-SHA256 hash |
| SQL injection protection | ✅ Parameterised queries | ✅ ORM (auto-parameterised) |
| XSS protection | ❌ No escaping (f-strings) | ✅ Jinja2 auto-escaping |
| CSRF protection | ❌ None | ❌ None |
| Input validation | ❌ None | ✅ Server-side checks |
| Session management | ⚠️ Manual, hardcoded key | ✅ Flask-Login, env-var key |
| Brute-force protection | ❌ None | ❌ None |
| Logout method | ❌ GET request | ❌ GET request |
| Debug mode | ❌ Enabled | ❌ Enabled |
| HTTPS | ❌ HTTP only | ❌ HTTP only |

---

*Both apps are learning tools. Neither should be deployed to the public internet without addressing the issues listed above.*
