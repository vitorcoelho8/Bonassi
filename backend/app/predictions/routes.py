from flask import Blueprint, g, jsonify, request

from app.participants.routes import login_required
from app.predictions.schemas import PredictionSchema
from app.predictions.service import PredictionService

predictions_bp = Blueprint("predictions", __name__)


@predictions_bp.get("/")
@login_required
def list_predictions():
    predictions = PredictionService().list_by_participant(g.current_user.id)
    return jsonify({"items": PredictionSchema().dump_many(predictions)})


@predictions_bp.post("/")
@login_required
def save_prediction():
    try:
        payload = PredictionSchema().load(request.get_json(silent=True) or {})
        prediction = PredictionService().upsert(g.current_user.id, payload)
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    return jsonify({"item": PredictionSchema().dump(prediction)}), 200
