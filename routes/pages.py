from flask import (
    Blueprint,
    render_template,
    request,
    jsonify,
    make_response
)

from extensions import db

from services.page_service import (
    get_page_by_name,
    create_page,
    update_page_text,
    is_owner
)


pages_bp = Blueprint("pages", __name__)


@pages_bp.route("/")
def home():

    return render_template(
        "index.html"
    )


@pages_bp.route("/<string:name>")
def open_page(name):

    page = get_page_by_name(name)

    if page is None:

        page, owner_secret = create_page(name)

        response = make_response(
            render_template(
                "page.html",
                page=page,
                is_owner=True,
                is_new_page=True
            )
        )

        response.set_cookie(
            "clonecat_owner",
            owner_secret,
            httponly=True,
            samesite="Lax"
        )

        return response

    owner_secret = request.cookies.get(
        "clonecat_owner"
    )

    owner = is_owner(
        page,
        owner_secret
    )

    return render_template(
        "page.html",
        page=page,
        is_owner=owner,
        is_new_page=False
    )

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

    owner_secret = request.cookies.get(
        "clonecat_owner"
    )

    if not is_owner(
        page,
        owner_secret
    ):
        return jsonify({
            "error": "Owner access required"
        }), 403

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400

    if "edit_locked" not in data:
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

@pages_bp.route("/manage/<string:name>")
def manage_page(name):

    page = get_page_by_name(name)

    if page is None:
        return "Page not found", 404

    owner_secret = request.cookies.get(
        "clonecat_owner"
    )

    if not is_owner(
        page,
        owner_secret
    ):
        return "Owner access required", 403

    return render_template(
        "manage.html",
        page=page
    )

@pages_bp.route(
    "/api/pages/<string:name>",
    methods=["PATCH"]
)
def update_page(name):

    page = get_page_by_name(name)

    if page is None:
        return jsonify({
            "error": "Page not found"
        }), 404

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400

    text = data.get("text")

    if text is None:
        return jsonify({
            "error": "Text is required"
        }), 400

    # Visitors can edit only when the page is unlocked.
    # Owner can edit even when locked.
    owner_secret = request.cookies.get(
        "clonecat_owner"
    )

    owner = is_owner(
        page,
        owner_secret
    )

    if page.edit_locked and not owner:
        return jsonify({
            "error": "Page is locked"
        }), 403

    page.text = text

    db.session.commit()

    return jsonify({
        "message": "Page updated successfully",
        "page": {
            "name": page.name,
            "text": page.text,
            "edit_locked": page.edit_locked
        }
    }), 200