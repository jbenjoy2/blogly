"""Models for Blogly."""
from flask_sqlalchemy import SQLAlchemy

DEFAULT_IMG_URL = 'https://www.freeiconspng.com/uploads/person-icon-user-person-man-icon-4.png'

db = SQLAlchemy()


def connect_db(app):
    db.app = app
    db.init_app(app)

# MODELS


class User(db.Model):
    """User class."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.Text, nullable=False)
    last_name = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.Text, nullable=False, default=DEFAULT_IMG_URL)

    @property
    def full_name(self):
        """render full firstname lastname" representation of user"""
        return f"{self.first_name} {self.last_name}"
