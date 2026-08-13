from flask import Blueprint, render_template, request, jsonify
from extensions import db

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

    if page.edit_locked:
        return jsonify({
            "error": "This page is read-only"
        }), 403

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

@pages_bp.route(
    "/api/pages/<string:name>/lock",
    methods=["PATCH"]
)
def update_edit_lock(name):

    page = get_page_by_name(name)

    if page is None:
        return jsonify({
            "error": "Page not found"
        }), 404

    data = request.get_json()

    if not data or "edit_locked" not in data:
        return jsonify({
            "error": "edit_locked is required"
        }), 400

    edit_locked = data["edit_locked"]

    if not isinstance(edit_locked, bool):
        return jsonify({
            "error": "edit_locked must be true or false"
        }), 400

    page.edit_locked = edit_locked

    db.session.commit()

    return jsonify({
        "message": "Edit lock updated",
        "edit_locked": page.edit_locked
    }), 200