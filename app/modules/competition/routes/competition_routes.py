from flask import Blueprint, jsonify, request

from app.modules.auth.auth import login_required
from app.modules.competition.schemas.competition_schema import CompetitionSchema
from app.modules.competition.services.competition_service import CompetitionService

competition_bp = Blueprint("competitions", __name__)


@competition_bp.get("/")
@login_required
def list_competitions():
    competitions = CompetitionService().list_active()
    return jsonify({"items": CompetitionSchema().dump_many(competitions)})


@competition_bp.post("/")
@login_required
def create_competition():
    try:
        payload = CompetitionSchema().load(request.get_json(silent=True) or {})
        competition = CompetitionService().create(payload)
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    return jsonify({"item": CompetitionSchema().dump(competition)}), 201
