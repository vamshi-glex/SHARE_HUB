from flask import Blueprint, render_template

from services.page_service import (
    get_page_by_name,
    create_page
)


pages_bp = Blueprint("pages", __name__)


@pages_bp.route("/")
def home():
    return render_template("index.html")


@pages_bp.route("/<string:name>")
def open_page(name):

    page = get_page_by_name(name)

    if page is None:
        page = create_page(name)

    return render_template(
        "page.html",
        page=page
    )