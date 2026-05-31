# config.py
# CSA Session 43 — Web Development Foundations
# Flask application configuration.

import os

class Config:
    # SECRET_KEY is used by Flask to sign session cookies.
    # In production this must be a long random string stored as an environment variable.
    SECRET_KEY = os.environ.get("SECRET_KEY", "csa-lab-dev-key-change-in-prod")

    # SQLite database stored in the instance/ folder
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///csa_lab.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
