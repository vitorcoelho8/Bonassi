from functools import wraps
from typing import Any, Callable

from flask import g, jsonify, request, session

from app.modules.auth.models.user_model import User


def get_bearer_token() -> str | None:
    auth_header = request.headers.get("Authorization", "")
    scheme, _, token = auth_header.partition(" ")

    if scheme.lower() != "bearer" or not token:
        return None

    return token


def login_required(view: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(view)
    def wrapper(*args: Any, **kwargs: Any):
        token = get_bearer_token()
        user_id = token or session.get("user_id")

        if not user_id:
            return jsonify({"error": "Authentication token is required."}), 401

        user = User.query.filter_by(id=user_id, is_active=True).first()
        if user is None:
            session.clear()
            return jsonify({"error": "Invalid authentication token."}), 401

        g.current_user = user
        g.access_token = user.id
        return view(*args, **kwargs)

    return wrapper


def is_authenticated() -> bool:
    user_id = session.get("user_id")

    if not user_id:
        return False

    user = User.query.filter_by(id=user_id, is_active=True).first()
    if user is None:
        session.clear()
        return False

    g.current_user = user
    return True
