from flask import Blueprint, g, jsonify, request
from sqlalchemy.exc import SQLAlchemyError

from app.bonus.schemas import BonusAnswerSchema
from app.bonus.service import BonusService
from app.database import db

bonus_bp = Blueprint("bonus", __name__)


@bonus_bp.get("")
@bonus_bp.get("/")
def list_bonus_answers():
    participant_id = request.args.get("participant_id") or getattr(g, "current_user", None)
    if hasattr(participant_id, "id"):
        participant_id = participant_id.id

    if not participant_id:
        return jsonify({"error": "participant_id e obrigatorio."}), 400

    answers = BonusService().list_by_participant(participant_id)
    return jsonify({"items": BonusAnswerSchema().dump_many(answers)})


@bonus_bp.get("/participant/<participant_id>")
def list_bonus_answers_by_participant(participant_id: str):
    answers = BonusService().list_by_participant(participant_id)
    return jsonify(BonusAnswerSchema().dump_many(answers))


@bonus_bp.post("")
@bonus_bp.post("/")
def save_bonus_answer():
    try:
        payload = BonusAnswerSchema().load(request.get_json(silent=True) or {})
        answer = BonusService().upsert(payload)
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "Banco de dados indisponivel."}), 503

    bonus = BonusAnswerSchema().dump(answer)
    return jsonify(
        {
            "message": "Solicitacao de bonus enviada para aprovacao.",
            "bonus": bonus,
            "item": bonus,
        }
    ), 201
