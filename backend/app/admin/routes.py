from flask import Blueprint, jsonify

from app.admin.schemas import AdminParticipantSchema
from app.admin.service import AdminService
from app.participants.routes import admin_required

admin_bp = Blueprint("admin", __name__)


@admin_bp.get("/participants")
@admin_required
def list_participants():
    participants = AdminService().list_participants()
    return jsonify({"items": AdminParticipantSchema().dump_many(participants)})
