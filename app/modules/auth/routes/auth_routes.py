from flask import Blueprint, current_app, jsonify, request, session
from sqlalchemy.exc import SQLAlchemyError

from app.database.extensions import db
from app.modules.auth.schemas.user_schema import LoginSchema, RegisterUserSchema
from app.modules.auth.services.auth_service import AuthService

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/register")
def register():
    try:
        payload = RegisterUserSchema().load(request.get_json(silent=True) or {})
        user = AuthService().register(payload)
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    return jsonify({"user": user.to_dict()}), 201


@auth_bp.post("/login")
def login():
    try:
        from app.database.bootstrap import ensure_default_admin

        ensure_default_admin()
        payload = LoginSchema().load(request.get_json(silent=True) or {})
        user = AuthService().authenticate(payload["email"], payload["password"])
    except ValueError as error:
        return jsonify({"error": str(error)}), 401
    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception("Database error during login.")
        return jsonify({"error": "Banco de dados indisponivel."}), 503

    session.clear()
    session["user_id"] = user.id
    session["user_email"] = user.email

    return jsonify({"user": user.to_dict(), "access_token": user.id})


@auth_bp.get("/me")
def me():
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"authenticated": False}), 401

    user = AuthService().user_repository.get_by_id(user_id)

    if not user or not user.is_active:
        session.clear()
        return jsonify({"authenticated": False}), 401

    return jsonify({"authenticated": True, "user": user.to_dict()})


@auth_bp.post("/logout")
def logout():
    session.clear()
    return jsonify({"status": "ok"})
