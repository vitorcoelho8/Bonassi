from app.database import db
from app.predictions.models import Prediction


class PredictionRepository:
    def list_by_participant(self, participant_id: str) -> list[Prediction]:
        return Prediction.query.filter_by(participant_id=participant_id).all()

    def get_for_match(self, participant_id: str, match_id: str) -> Prediction | None:
        return Prediction.query.filter_by(participant_id=participant_id, match_id=match_id).first()

    def save(self, prediction: Prediction) -> Prediction:
        db.session.add(prediction)
        db.session.commit()
        return prediction


class PredictionService:
    def __init__(self, repository: PredictionRepository | None = None) -> None:
        self.repository = repository or PredictionRepository()

    def list_by_participant(self, participant_id: str) -> list[Prediction]:
        return self.repository.list_by_participant(participant_id)

    def upsert(self, participant_id: str, data: dict) -> Prediction:
        prediction = self.repository.get_for_match(participant_id, data["match_id"])

        if prediction is None:
            prediction = Prediction(participant_id=participant_id, match_id=data["match_id"])

        prediction.home_score = data["home_score"]
        prediction.away_score = data["away_score"]

        return self.repository.save(prediction)
