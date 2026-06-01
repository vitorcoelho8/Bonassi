from sqlalchemy import and_, case, func

from app.bonus.models import BonusAnswer
from app.database import db
from app.matches.models import Match
from app.matches.phases import phase_label
from app.participants.models import Participant
from app.predictions.models import Prediction
from app.teams.models import Team


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

    def list_round(self) -> dict:
        match = self._last_finished_brazil_match()
        if match is None:
            return {
                "match": None,
                "ranking": [],
                "message": "Nenhuma partida finalizada ainda.",
            }

        return {
            "match": self._round_match_payload(match),
            "ranking": self._round_ranking(match),
        }

    def _prediction_points(self) -> dict[str, dict[str, int]]:
        rows = (
            db.session.query(
                Prediction.participant_id,
                func.coalesce(
                    func.sum(
                        case(
                            (
                                and_(
                                    Prediction.home_score == Match.home_score,
                                    Prediction.away_score == Match.away_score,
                                ),
                                1,
                            ),
                            else_=0,
                        )
                    ),
                    0,
                ).label("exact_scores"),
                func.coalesce(func.sum(Prediction.points), 0).label("points"),
            )
            .join(Match)
            .filter(func.upper(Match.status) == "FINISHED")
            .group_by(Prediction.participant_id)
            .all()
        )

        return {
            participant_id: {"exact_scores": int(exact_scores or 0), "points": int(points or 0)}
            for participant_id, exact_scores, points in rows
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

    def _last_finished_brazil_match(self) -> Match | None:
        return (
            Match.query.filter(func.upper(Match.status) == "FINISHED")
            .filter(Match.is_brazil_match.is_(True))
            .filter(Match.home_score.isnot(None))
            .filter(Match.away_score.isnot(None))
            .filter(Match.starts_at.isnot(None))
            .order_by(Match.starts_at.desc())
            .first()
        )

    def _round_match_payload(self, match: Match) -> dict:
        teams = self._teams_by_name([match.home_team, match.away_team])
        home_team = teams.get(match.home_team)
        away_team = teams.get(match.away_team)

        return {
            "id": match.id,
            "home_team": match.home_team,
            "away_team": match.away_team,
            "home_score": match.home_score,
            "away_score": match.away_score,
            "starts_at": match.starts_at.isoformat() if match.starts_at else None,
            "phase": match.phase,
            "phase_label": phase_label(match.phase),
            "home_flag_url": home_team.flag_url if home_team else None,
            "away_flag_url": away_team.flag_url if away_team else None,
            "display_score": (
                f"{match.home_team} {match.home_score} x {match.away_score} {match.away_team}"
            ),
        }

    def _round_ranking(self, match: Match) -> list[dict]:
        rows = (
            db.session.query(Prediction, Participant)
            .join(Participant, Prediction.participant_id == Participant.id)
            .filter(Prediction.match_id == match.id)
            .filter(Participant.is_active.is_(True))
            .filter(Participant.role == "participant")
            .order_by(Prediction.points.desc(), Participant.name.asc())
            .all()
        )

        ranking = []
        for position, (prediction, participant) in enumerate(rows, start=1):
            ranking.append(
                {
                    "position": position,
                    "participant_id": participant.id,
                    "name": participant.name,
                    "points": int(prediction.points or 0),
                    "exact": (
                        prediction.home_score == match.home_score
                        and prediction.away_score == match.away_score
                    ),
                    "predicted_score": (
                        f"{match.home_team} {prediction.home_score} x "
                        f"{prediction.away_score} {match.away_team}"
                    ),
                }
            )

        return ranking

    def _teams_by_name(self, names: list[str]) -> dict[str, Team]:
        rows = Team.query.filter(Team.name.in_(names)).all()
        return {team.name: team for team in rows}
