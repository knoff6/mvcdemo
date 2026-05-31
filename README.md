# Session 43 — Web Development Foundations


Lab files for Session 43. Two Flask applications that demonstrate how a web application is structured — starting from the bare minimum and building up to a proper MVC architecture.

---

## Getting Started

```bash
# Clone the repository
git clone https://github.com/knoff6/mvcdemo

# Enter the folder
cd mvcdemo

# Create a virtual environment
python -m venv venv

# Activate — Linux / macOS
source venv/bin/activate

# Activate — Windows
venv\Scripts\activate
```

Your prompt will show `(venv)` to confirm it's active. All installs from this point go into the venv, not your system Python. To deactivate when done:

```bash
deactivate
```

---

## What's Inside

```
├── basic.py              # App 1 — bare minimum Flask app
└── mvc_app/              # App 2 — full MVC Flask app
    ├── app.py            # Controller — routes and request handling
    ├── models.py         # Model — database schema and queries
    ├── config.py         # App configuration
    ├── requirements.txt  # Python dependencies
    ├── templates/        # View — Jinja2 HTML templates
    │   ├── base.html
    │   ├── login.html
    │   ├── register.html
    │   ├── dashboard.html
    │   ├── post.html
    │   ├── search.html
    │   └── admin.html
    └── static/
        ├── css/style.css
        └── js/main.js
```

---

## App 1 — Basic App

A single-file Flask application. Register, login, get welcomed by name. No frameworks, no ORM, no styling — just Flask and Python's built-in `sqlite3`.

The point of this app is to show what a web app looks like at its most stripped-down. Every line is visible and traceable with no abstractions in the way.

**Run:**

```bash
python basic.py
```

Open `http://localhost:5002`

**No install needed beyond Flask:**

```bash
pip install flask
```

---

## App 2 — MVC App (`mvc_app`)

A structured Flask application following the MVC (Model-View-Controller) pattern. Same core features as the minimal app — register, login, dashboard — but with proper separation of concerns, styling, and a real ORM.

**The three layers:**

| Layer | File(s) | Responsibility |
|---|---|---|
| Model | `models.py` | Database schema, queries, password hashing |
| View | `templates/*.html` | HTML pages rendered by Jinja2 |
| Controller | `app.py` | Routes, input validation, wiring M and V together |

**Setup and run:**

```bash
cd mvc_app
pip install -r requirements.txt
flask run --debug
```

Open `http://localhost:5000`

The database is created and seeded automatically on first run with three users:

| Username | Password | Role |
|---|---|---|
| admin | Admin1234! | admin |
| alice | AlicePass1! | user |
| bob | BobPass1! | user |

---

## Comparison

| | `basic.py` | `mvc_app` |
|---|---|---|
| Files | 1 | 13 |
| Lines of code | ~135 | ~600 |
| Architecture | None | MVC |
| Database access | Raw `sqlite3` | SQLAlchemy ORM |
| Templates | Inline HTML strings | Separate Jinja2 files |
| Styling | None | CSS stylesheet |
| Password storage | Plaintext | PBKDF2-SHA256 hash |

---

## Prerequisites

- Python 3.10 or higher
- pip

Both apps were built and tested on Python 3.11.

---

*A teaching resource for anyone learning web development and web application security.*
