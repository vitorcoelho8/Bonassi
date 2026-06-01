from flask import Blueprint, jsonify

from app.participants.routes import login_required
from app.teams.schemas import TeamSchema
from app.teams.service import TeamService

teams_bp = Blueprint("teams", __name__)


@teams_bp.get("")
@teams_bp.get("/")
@login_required
def list_teams():
    teams = TeamService().list_all()
    return jsonify(TeamSchema().dump_many(teams))


@teams_bp.get("/active")
@login_required
def list_active_teams():
    teams = TeamService().list_active_opponents()
    return jsonify(TeamSchema().dump_many(teams))
