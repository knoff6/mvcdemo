# config.py
# Settings for the Flask app. Keeping them in one place makes it easy
# to find and change them later.

import os

class Config:
    # Flask uses this key to keep track of who is logged in (via cookies).
    SECRET_KEY = os.environ.get("SECRET_KEY", "csa-lab-dev-key-change-in-prod")

    # Where the database file is stored. SQLite keeps everything in one file.
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///csa_lab.db"
    )

    # Turn off a SQLAlchemy feature we don't need (saves memory).
    SQLALCHEMY_TRACK_MODIFICATIONS = False
