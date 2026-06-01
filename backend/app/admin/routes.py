from flask import Blueprint, jsonify, request
from sqlalchemy.exc import SQLAlchemyError

from app.admin.schemas import AdminParticipantSchema
from app.admin.service import AdminService
from app.bonus.schemas import BonusAnswerSchema
from app.bonus.service import BonusService
from app.database import db
from app.matches.schemas import MatchSchema
from app.participants.routes import admin_required

admin_bp = Blueprint("admin", __name__)


@admin_bp.get("/participants")
@admin_required
def list_participants():
    participants = AdminService().list_participants()
    return jsonify({"items": AdminParticipantSchema().dump_many(participants)})


@admin_bp.get("/matches/phases")
@admin_required
def list_next_match_phases():
    return jsonify(AdminService().list_next_match_phases())


@admin_bp.post("/matches/next-brazil-match")
@admin_required
def create_next_brazil_match():
    try:
        match = AdminService().create_next_brazil_match(request.get_json(silent=True) or {})
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "Banco de dados indisponivel."}), 503

    return jsonify(
        {
            "message": "Proxima partida do Brasil criada com sucesso.",
            "match": MatchSchema().dump(match),
        }
    ), 201


@admin_bp.put("/matches/<match_id>/result")
@admin_required
def save_match_result(match_id: str):
    try:
        match, updated_predictions = AdminService().save_match_result(
            match_id,
            request.get_json(silent=True) or {},
        )
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "Banco de dados indisponivel."}), 503

    return jsonify(
        {
            "message": "Resultado salvo e pontuação recalculada com sucesso.",
            "match": {
                "id": match.id,
                "home_team": match.home_team,
                "away_team": match.away_team,
                "home_score": match.home_score,
                "away_score": match.away_score,
                "status": match.status.upper() if match.status else match.status,
            },
            "updated_predictions": updated_predictions,
        }
    )


@admin_bp.get("/bonus/pending")
@admin_required
def list_pending_bonus():
    answers = BonusService().list_pending()
    return jsonify(BonusAnswerSchema().dump_many(answers, include_participant=True))


@admin_bp.patch("/bonus/<bonus_id>/approve")
@admin_required
def approve_bonus(bonus_id: str):
    try:
        answer = BonusService().approve(bonus_id)
    except ValueError as error:
        return jsonify({"error": str(error)}), 404
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "Banco de dados indisponivel."}), 503

    bonus = BonusAnswerSchema().dump(answer)
    return jsonify(
        {
            "message": "Bonus aprovado com sucesso.",
            "bonus": bonus,
            "item": bonus,
        }
    )


@admin_bp.patch("/bonus/<bonus_id>/reject")
@admin_required
def reject_bonus(bonus_id: str):
    try:
        answer = BonusService().reject(bonus_id)
    except ValueError as error:
        return jsonify({"error": str(error)}), 404
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "Banco de dados indisponivel."}), 503

    bonus = BonusAnswerSchema().dump(answer)
    return jsonify(
        {
            "message": "Bonus recusado com sucesso.",
            "bonus": bonus,
            "item": bonus,
        }
    )
