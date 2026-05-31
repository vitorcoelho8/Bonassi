from flask import Blueprint, jsonify, request

from app.matches.schemas import MatchSchema
from app.matches.service import MatchService
from app.participants.routes import admin_required, login_required

matches_bp = Blueprint("matches", __name__)


@matches_bp.get("/")
@login_required
def list_matches():
    matches = MatchService().list_active()
    return jsonify({"items": MatchSchema().dump_many(matches)})


@matches_bp.post("/")
@admin_required
def create_match():
    try:
        payload = MatchSchema().load(request.get_json(silent=True) or {})
        match = MatchService().create(payload)
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    return jsonify({"item": MatchSchema().dump(match)}), 201
