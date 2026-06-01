from flask import Blueprint, g, jsonify, request
from sqlalchemy.exc import SQLAlchemyError

from app.database import db
from app.participants.routes import admin_required
from app.predictions.schemas import PredictionSchema
from app.predictions.service import PredictionService

predictions_bp = Blueprint("predictions", __name__)


@predictions_bp.get("")
@predictions_bp.get("/")
@admin_required
def list_predictions():
    participant_id = request.args.get("participant_id") or getattr(g, "current_user", None)
    if hasattr(participant_id, "id"):
        participant_id = participant_id.id

    if not participant_id:
        return jsonify({"error": "participant_id e obrigatorio."}), 400

    predictions = PredictionService().list_by_participant(participant_id)
    return jsonify({"items": PredictionSchema().dump_many(predictions)})


@predictions_bp.get("/participant/<participant_id>")
@admin_required
def list_predictions_by_participant(participant_id: str):
    predictions = PredictionService().list_by_participant(participant_id)
    return jsonify({"items": PredictionSchema().dump_many(predictions)})


@predictions_bp.post("")
@predictions_bp.post("/")
@admin_required
def save_prediction():
    try:
        payload = PredictionSchema().load(request.get_json(silent=True) or {})
        prediction = PredictionService().create(payload)
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "Banco de dados indisponivel."}), 503

    return jsonify({"item": PredictionSchema().dump(prediction)}), 201


@predictions_bp.put("/<prediction_id>")
@admin_required
def update_prediction(prediction_id: str):
    try:
        payload = PredictionSchema().load(request.get_json(silent=True) or {})
        prediction = PredictionService().update(prediction_id, payload)
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "Banco de dados indisponivel."}), 503

    return jsonify({"item": PredictionSchema().dump(prediction)}), 200
