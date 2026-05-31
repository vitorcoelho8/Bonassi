from sqlalchemy import func

from app.bonus.models import BonusAnswer
from app.database import db
from app.matches.models import Match
from app.participants.models import Participant
from app.predictions.models import Prediction


class RankingService:
    def list_global(self) -> list[dict]:
        prediction_points = self._prediction_points()
        bonus_points = self._bonus_points()
        participants = (
            Participant.query.filter_by(is_active=True, role="participant")
            .order_by(Participant.name)
            .all()
        )

        ranking = []
        for participant in participants:
            exact_scores = prediction_points.get(participant.id, {}).get("exact_scores", 0)
            points = prediction_points.get(participant.id, {}).get("points", 0)
            points += bonus_points.get(participant.id, 0)
            ranking.append(
                {
                    "participant": participant.to_dict(),
                    "exact_scores": exact_scores,
                    "points": points,
                }
            )

        return sorted(ranking, key=lambda item: item["points"], reverse=True)

    def _prediction_points(self) -> dict[str, dict[str, int]]:
        rows = (
            db.session.query(
                Prediction.participant_id,
                func.count(Prediction.id).label("exact_scores"),
            )
            .join(Match)
            .filter(func.upper(Match.status) == "FINISHED")
            .filter(Prediction.home_score == Match.home_score)
            .filter(Prediction.away_score == Match.away_score)
            .group_by(Prediction.participant_id)
            .all()
        )

        return {
            participant_id: {"exact_scores": exact_scores, "points": exact_scores * 10}
            for participant_id, exact_scores in rows
        }

    def _bonus_points(self) -> dict[str, int]:
        rows = (
            db.session.query(
                BonusAnswer.participant_id,
                func.coalesce(func.sum(BonusAnswer.points), 0),
            )
            .filter(func.upper(BonusAnswer.status) == "APPROVED")
            .group_by(BonusAnswer.participant_id)
            .all()
        )

        return {participant_id: int(points or 0) for participant_id, points in rows}
