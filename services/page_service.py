import hashlib
import secrets
from datetime import datetime, timedelta

from models import Page
from extensions import db


def get_page_by_name(name):
    return Page.query.filter_by(name=name).first()


def generate_owner_secret():
    return secrets.token_urlsafe(32)


def hash_owner_secret(secret):
    return hashlib.sha256(
        secret.encode()
    ).hexdigest()


def create_page(name):

    owner_secret = generate_owner_secret()

    owner_secret_hash = hash_owner_secret(
        owner_secret
    )

    expires_at = (
        datetime.utcnow()
        + timedelta(days=7)
    )

    page = Page(
        name=name,
        owner_token_hash=owner_secret_hash,
        expires_at=expires_at
    )

    db.session.add(page)

    db.session.commit()

    return page, owner_secret

def is_owner(page, owner_secret):

    if not owner_secret:
        return False

    secret_hash = hash_owner_secret(
        owner_secret
    )

    return secrets.compare_digest(
        secret_hash,
        page.owner_token_hash
    )


def update_page_text(page, text):

    page.text = text

    db.session.commit()

    return page

def is_page_expired(page):

    if page.expires_at is None:
        return False

    return datetime.utcnow() >= page.expires_at