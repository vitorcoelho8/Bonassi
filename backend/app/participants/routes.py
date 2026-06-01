from functools import wraps
from typing import Any, Callable

from flask import Blueprint, current_app, g, jsonify, request, session
from sqlalchemy.exc import SQLAlchemyError
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from app.database import db
from app.participants.schemas import LoginSchema, ParticipantSchema
from app.participants.service import ParticipantService

participants_bp = Blueprint("participants", __name__)


def generate_access_token(user_id: str) -> str:
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    return serializer.dumps({"user_id": user_id}, salt=current_app.config["AUTH_TOKEN_SALT"])


def verify_access_token(token: str) -> str | None:
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    try:
        payload = serializer.loads(
            token,
            salt=current_app.config["AUTH_TOKEN_SALT"],
            max_age=current_app.config["AUTH_TOKEN_MAX_AGE_SECONDS"],
        )
    except (BadSignature, SignatureExpired):
        return None

    user_id = payload.get("user_id") if isinstance(payload, dict) else None
    return str(user_id) if user_id else None


def get_bearer_token() -> str | None:
    auth_header = request.headers.get("Authorization", "")
    scheme, _, token = auth_header.partition(" ")

    if scheme.lower() != "bearer" or not token:
        return None

    return token


def login_required(view: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(view)
    def wrapper(*args: Any, **kwargs: Any):
        bearer_token = get_bearer_token()
        user_id = verify_access_token(bearer_token) if bearer_token else session.get("user_id")

        if not user_id:
            return jsonify({"error": "Authentication token is required."}), 401

        participant = ParticipantService().get_by_id(user_id)
        if participant is None or not participant.is_active:
            session.clear()
            return jsonify({"error": "Invalid authentication token."}), 401

        g.current_user = participant
        g.access_token = bearer_token
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


@participants_bp.get("")
@participants_bp.get("/")
@admin_required
def list_participants():
    participants = ParticipantService().list_active()
    return jsonify({"items": ParticipantSchema().dump_many(participants)})


@participants_bp.get("/search")
@admin_required
def search_participants():
    term = request.args.get("term", "")
    participants = ParticipantService().search(term)
    return jsonify({"items": ParticipantSchema().dump_many(participants)})


@participants_bp.get("/<participant_id>")
@admin_required
def get_participant(participant_id: str):
    participant = ParticipantService().get_by_id(participant_id)

    if participant is None or not participant.is_active or participant.role != "participant":
        return jsonify({"error": "Participante nao encontrado."}), 404

    return jsonify({"item": ParticipantSchema().dump(participant)})


@participants_bp.post("")
@participants_bp.post("/")
@admin_required
def create_participant():
    try:
        payload = ParticipantSchema().load(request.get_json(silent=True) or {})
        participant = ParticipantService().register(payload)
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "Banco de dados indisponivel."}), 503

    return jsonify({"item": ParticipantSchema().dump(participant)}), 201


@participants_bp.post("/register")
@admin_required
def register():
    try:
        payload = ParticipantSchema().load(request.get_json(silent=True) or {})
        participant = ParticipantService().register(payload)
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "Banco de dados indisponivel."}), 503
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    return jsonify({"user": ParticipantSchema().dump(participant), "item": ParticipantSchema().dump(participant)}), 201


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
    session.permanent = True
    session["user_id"] = participant.id
    session["user_email"] = participant.email

    return jsonify({"user": participant.to_dict(), "access_token": generate_access_token(participant.id)})


@participants_bp.get("/me")
@login_required
def me():
    return jsonify({"authenticated": True, "user": g.current_user.to_dict()})


@participants_bp.post("/logout")
def logout():
    session.clear()
    return jsonify({"status": "ok"})
