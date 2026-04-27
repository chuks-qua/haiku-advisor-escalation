"""Auth API. Login issues a 1-day session token."""
from __future__ import annotations

from flask import Blueprint, current_app, jsonify, request

from services.auth import authenticate, issue_session_token, register
from services.validation import validate_signup

bp = Blueprint("auth", __name__)


@bp.post("/login")
def login():
    body = request.get_json() or {}
    user = authenticate(body.get("email", ""), body.get("password", ""))
    if user is None:
        return jsonify({"error": "invalid credentials"}), 401
    token = issue_session_token(user, current_app.config["SECRET_KEY"])
    return jsonify({"token": token, "user_id": user.id})


@bp.post("/register")
def signup():
    body = request.get_json() or {}
    errors = validate_signup(body)
    if errors:
        return jsonify({"errors": errors}), 400
    user = register(body["email"], body["password"], body.get("phone"))
    return jsonify({"id": user.id, "email": user.email}), 201
