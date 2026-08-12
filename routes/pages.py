from flask import Blueprint, render_template, request, jsonify

from services.page_service import (
    get_page_by_name,
    create_page,
    update_page_text
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


@pages_bp.route("/api/pages/<string:name>", methods=["PATCH"])
def update_page(name):

    page = get_page_by_name(name)

    if page is None:
        return jsonify({
            "error": "Page not found"
        }), 404

    data = request.get_json()

    if not data or "text" not in data:
        return jsonify({
            "error": "Text is required"
        }), 400

    page = update_page_text(
        page,
        data["text"]
    )

    return jsonify({
        "message": "Page updated successfully",
        "page": {
            "name": page.name,
            "text": page.text,
            "edit_locked": page.edit_locked
        }
    }), 200