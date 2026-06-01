from datetime import datetime, timezone

from app.database import db
from app.matches.models import Match
from app.participants.models import Participant
from app.predictions.models import Prediction


def get_match_result(home_score: int, away_score: int) -> str:
    if home_score > away_score:
        return "HOME_WIN"
    if home_score < away_score:
        return "AWAY_WIN"
    return "DRAW"


def calculate_match_points(
    predicted_home: int,
    predicted_away: int,
    real_home: int,
    real_away: int,
) -> int:
    if predicted_home == real_home and predicted_away == real_away:
        return 8

    points = 0
    predicted_result = get_match_result(predicted_home, predicted_away)
    real_result = get_match_result(real_home, real_away)

    if predicted_result == real_result:
        points += 6

    if not _picked_opposite_winner(predicted_result, real_result) and (
        predicted_home == real_home or predicted_away == real_away
    ):
        points += 1

    return points


def _picked_opposite_winner(predicted_result: str, real_result: str) -> bool:
    return {predicted_result, real_result} == {"HOME_WIN", "AWAY_WIN"}


class PredictionRepository:
    def list_by_participant(self, participant_id: str) -> list[Prediction]:
        return Prediction.query.filter_by(participant_id=participant_id).all()

    def get_for_match(self, participant_id: str, match_id: str) -> Prediction | None:
        return Prediction.query.filter_by(participant_id=participant_id, match_id=match_id).first()

    def get_by_id(self, prediction_id: str) -> Prediction | None:
        return db.session.get(Prediction, prediction_id)

    def save(self, prediction: Prediction) -> Prediction:
        db.session.add(prediction)
        db.session.commit()
        return prediction


class PredictionService:
    def __init__(self, repository: PredictionRepository | None = None) -> None:
        self.repository = repository or PredictionRepository()

    def list_by_participant(self, participant_id: str) -> list[Prediction]:
        return self.repository.list_by_participant(participant_id)

    def create(self, data: dict) -> Prediction:
        participant = self._get_valid_participant(data["participant_id"])
        match = self._get_valid_match(data["match_id"])
        self._ensure_match_is_open(match)

        if self.repository.get_for_match(participant.id, match.id):
            raise ValueError("Este participante ja possui palpite para este jogo.")

        prediction = Prediction(
            participant_id=participant.id,
            match_id=match.id,
            points=0,
        )
        prediction.home_score = data["home_score"]
        prediction.away_score = data["away_score"]

        return self.repository.save(prediction)

    def update(self, prediction_id: str, data: dict) -> Prediction:
        prediction = self.repository.get_by_id(prediction_id)
        if prediction is None:
            raise ValueError("Palpite nao encontrado.")

        if prediction.participant_id != data["participant_id"]:
            raise ValueError("O palpite informado nao pertence ao participante selecionado.")

        match = self._get_valid_match(prediction.match_id)
        self._ensure_match_is_open(match)

        prediction.home_score = data["home_score"]
        prediction.away_score = data["away_score"]
        return self.repository.save(prediction)

    def _get_valid_participant(self, participant_id: str) -> Participant:
        participant = db.session.get(Participant, participant_id)
        if participant is None or not participant.is_active or participant.role != "participant":
            raise ValueError("Participante nao encontrado.")

        return participant

    def _get_valid_match(self, match_id: str) -> Match:
        match = db.session.get(Match, match_id)
        if match is None or not match.is_active:
            raise ValueError("Jogo nao encontrado.")

        return match

    def _ensure_match_is_open(self, match: Match) -> None:
        if match.starts_at is None:
            raise ValueError("Horario do jogo nao cadastrado.")

        now = datetime.now(timezone.utc)
        starts_at = match.starts_at
        if starts_at.tzinfo is None:
            now = now.replace(tzinfo=None)

        if starts_at <= now:
            raise ValueError("O prazo para palpitar neste jogo ja terminou.")
