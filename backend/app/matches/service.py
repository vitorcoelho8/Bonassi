from datetime import datetime, timezone

from sqlalchemy import func

from app.database import db
from app.matches.models import Match


class MatchRepository:
    def list_active(self) -> list[Match]:
        return Match.query.filter_by(is_active=True).order_by(Match.starts_at.asc()).all()

    def get_by_id(self, match_id: str) -> Match | None:
        return db.session.get(Match, match_id)

    def get_next(self) -> Match | None:
        return (
            Match.query.filter_by(is_active=True)
            .filter(Match.starts_at.isnot(None))
            .filter(Match.starts_at > datetime.now(timezone.utc))
            .filter(func.upper(Match.status) == "SCHEDULED")
            .order_by(Match.starts_at.asc())
            .first()
        )

    def create(self, match: Match) -> Match:
        db.session.add(match)
        db.session.commit()
        return match


class MatchService:
    def __init__(self, repository: MatchRepository | None = None) -> None:
        self.repository = repository or MatchRepository()

    def list_active(self) -> list[Match]:
        return self.repository.list_active()

    def get_by_id(self, match_id: str) -> Match | None:
        return self.repository.get_by_id(match_id)

    def get_next(self) -> Match | None:
        return self.repository.get_next()

    def create(self, data: dict) -> Match:
        match = Match(**data)
        return self.repository.create(match)
