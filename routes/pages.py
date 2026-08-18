from flask import (
    Blueprint,
    render_template,
    request,
    jsonify,
    make_response
)

from sqlalchemy.exc import SQLAlchemyError

import re

from extensions import db

from services.page_service import (
    get_page_by_name,
    create_page,
    is_owner,
    is_page_expired
)


pages_bp = Blueprint("pages", __name__)


# -------------------------
# PAGE NAME VALIDATION
# -------------------------

PAGE_NAME_PATTERN = re.compile(
    r"^[A-Za-z0-9_-]{1,50}$"
)


def is_valid_page_name(name):
    return bool(
        PAGE_NAME_PATTERN.fullmatch(name)
    )


# -------------------------
# HOME
# -------------------------

@pages_bp.route("/")
def home():

    return render_template(
        "index.html"
    )


# -------------------------
# OPEN PAGE
# -------------------------

@pages_bp.route("/<string:name>")
def open_page(name):

    # Validate page name
    if not is_valid_page_name(name):

        return render_template(
            "invalid_page.html",
            message="Invalid page name"
        ), 400

    page = get_page_by_name(name)

    # -------------------------
    # EXPIRED PAGE
    # -------------------------

    if page is not None and is_page_expired(page):

        db.session.delete(page)
        db.session.commit()

        page = None

    # -------------------------
    # CREATE NEW PAGE
    # -------------------------

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
            samesite="Lax",
            secure=request.is_secure,
            path="/"
        )

        return response

    # -------------------------
    # EXISTING PAGE
    # -------------------------

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


# -------------------------
# UPDATE PAGE TEXT
# -------------------------

@pages_bp.route(
    "/api/pages/<string:name>",
    methods=["PATCH"]
)
def update_page(name):

    # Validate page name
    if not is_valid_page_name(name):

        return jsonify({
            "error": "Invalid page name"
        }), 400

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

    # Text must be a string
    if not isinstance(text, str):

        return jsonify({
            "error": "Text must be a string"
        }), 400

    # Maximum 100,000 characters
    if len(text) > 100000:

        return jsonify({
            "error": "Text cannot exceed 100,000 characters"
        }), 400

    # -------------------------
    # CHECK OWNER
    # -------------------------

    owner_secret = request.cookies.get(
        "clonecat_owner"
    )

    owner = is_owner(
        page,
        owner_secret
    )

    print(
    "AUTH DEBUG:",
    "page=", page.name,
    "locked=", page.edit_locked,
    "owner_cookie_present=", bool(owner_secret),
    "is_owner=", owner
)

    # Locked page → only owner can edit
    if page.edit_locked and not owner:

        return jsonify({
            "error": "Page is locked"
        }), 403

    # -------------------------
    # UPDATE DATABASE
    # -------------------------

    page.text = text

    try:

        db.session.commit()

    except SQLAlchemyError as e:

        db.session.rollback()

        print(
            "DATABASE ERROR:",
            e
        )

        return jsonify({
            "error": "Could not save the page"
        }), 500

    # -------------------------
    # SUCCESS
    # -------------------------

    return jsonify({
        "message": "Page updated successfully"
    }), 200


# -------------------------
# ABOUT
# -------------------------

@pages_bp.route("/about")
def about():

    return render_template(
        "about.html"
    )


# -------------------------
# FEATURES
# -------------------------

@pages_bp.route("/features")
def features():

    return render_template(
        "features.html"
    )


# -------------------------
# OWNER MANAGEMENT PAGE
# -------------------------

@pages_bp.route(
    "/manage/<string:name>"
)
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


# -------------------------
# LOCK / UNLOCK PAGE
# -------------------------

@pages_bp.route(
    "/api/pages/<string:name>/lock",
    methods=["PATCH"]
)
def update_edit_lock(name):

    # Validate page name
    if not is_valid_page_name(name):

        return jsonify({
            "error": "Invalid page name"
        }), 400

    page = get_page_by_name(name)

    if page is None:

        return jsonify({
            "error": "Page not found"
        }), 404

    # -------------------------
    # CHECK OWNER
    # -------------------------

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

    # -------------------------
    # GET REQUEST DATA
    # -------------------------

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

    # Must be boolean
    if not isinstance(
        edit_locked,
        bool
    ):

        return jsonify({
            "error": "edit_locked must be true or false"
        }), 400

    # -------------------------
    # UPDATE DATABASE
    # -------------------------

    page.edit_locked = edit_locked

    try:

        db.session.commit()

    except SQLAlchemyError as e:

        db.session.rollback()

        print(
            "DATABASE ERROR:",
            e
        )

        return jsonify({
            "error": "Could not update lock status"
        }), 500

    # -------------------------
    # SUCCESS
    # -------------------------

    return jsonify({
        "message": "Edit lock updated",
        "edit_locked": page.edit_locked
    }), 200