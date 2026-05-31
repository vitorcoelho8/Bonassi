from flask import Blueprint, g, jsonify, request

from app.bonus.schemas import BonusAnswerSchema
from app.bonus.service import BonusService
from app.participants.routes import login_required

bonus_bp = Blueprint("bonus", __name__)


@bonus_bp.get("/")
@login_required
def list_bonus_answers():
    answers = BonusService().list_by_participant(g.current_user.id)
    return jsonify({"items": BonusAnswerSchema().dump_many(answers)})


@bonus_bp.post("/")
@login_required
def save_bonus_answer():
    try:
        payload = BonusAnswerSchema().load(request.get_json(silent=True) or {})
        answer = BonusService().upsert(g.current_user.id, payload)
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    return jsonify({"item": BonusAnswerSchema().dump(answer)}), 200
