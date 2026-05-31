from functools import wraps
from typing import Any, Callable

from flask import Blueprint, g, jsonify, request, session
from sqlalchemy.exc import SQLAlchemyError

from app.database import db
from app.participants.schemas import LoginSchema, ParticipantSchema
from app.participants.service import ParticipantService

participants_bp = Blueprint("participants", __name__)


def get_bearer_token() -> str | None:
    auth_header = request.headers.get("Authorization", "")
    scheme, _, token = auth_header.partition(" ")

    if scheme.lower() != "bearer" or not token:
        return None

    return token


def login_required(view: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(view)
    def wrapper(*args: Any, **kwargs: Any):
        user_id = get_bearer_token() or session.get("user_id")

        if not user_id:
            return jsonify({"error": "Authentication token is required."}), 401

        participant = ParticipantService().get_by_id(user_id)
        if participant is None or not participant.is_active:
            session.clear()
            return jsonify({"error": "Invalid authentication token."}), 401

        g.current_user = participant
        g.access_token = participant.id
        return view(*args, **kwargs)

    return wrapper


def admin_required(view: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(view)
    @login_required
    def wrapper(*args: Any, **kwargs: Any):
        if g.current_user.role != "admin":
            return jsonify({"error": "Admin access is required."}), 403

        return view(*args, **kwargs)

    return wrapper


@participants_bp.get("/")
@login_required
def list_participants():
    participants = ParticipantService().list_active()
    return jsonify({"items": ParticipantSchema().dump_many(participants)})


@participants_bp.post("/register")
def register():
    try:
        payload = ParticipantSchema().load(request.get_json(silent=True) or {})
        participant = ParticipantService().register(payload)
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    return jsonify({"user": ParticipantSchema().dump(participant)}), 201


@participants_bp.post("/login")
def login():
    try:
        payload = LoginSchema().load(request.get_json(silent=True) or {})
        participant = ParticipantService().authenticate(payload["email"], payload["password"])
    except ValueError as error:
        return jsonify({"error": str(error)}), 401
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "Banco de dados indisponivel."}), 503

    session.clear()
    session["user_id"] = participant.id
    session["user_email"] = participant.email

    return jsonify({"user": participant.to_dict(), "access_token": participant.id})


@participants_bp.get("/me")
def me():
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"authenticated": False}), 401

    participant = ParticipantService().get_by_id(user_id)

    if not participant or not participant.is_active:
        session.clear()
        return jsonify({"authenticated": False}), 401

    return jsonify({"authenticated": True, "user": participant.to_dict()})


@participants_bp.post("/logout")
def logout():
    session.clear()
    return jsonify({"status": "ok"})
