from models import Page
from extensions import db


def get_page_by_name(name):
    return Page.query.filter_by(name=name).first()


def create_page(name):
    page = Page(name=name)

    db.session.add(page)
    db.session.commit()

    return page