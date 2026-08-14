from datetime import datetime
from extensions import db

class Page(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    text = db.Column(
        db.Text,
        default=""
    )

    edit_locked = db.Column(
        db.Boolean,
        default=False
    )

    owner_token_hash = db.Column(
        db.String(128),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    expires_at = db.Column(
        db.DateTime,
        nullable=True
    )