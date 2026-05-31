from flask import Blueprint, jsonify

from app.participants.routes import login_required
from app.ranking.service import RankingService

ranking_bp = Blueprint("ranking", __name__)


@ranking_bp.get("/")
@login_required
def global_ranking():
    return jsonify({"items": RankingService().list_global()})
