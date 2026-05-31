from app.database import db
from app.matches.models import Match


class MatchRepository:
    def list_active(self) -> list[Match]:
        return Match.query.filter_by(is_active=True).order_by(Match.starts_at.asc()).all()

    def get_by_id(self, match_id: str) -> Match | None:
        return db.session.get(Match, match_id)

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

    def create(self, data: dict) -> Match:
        match = Match(**data)
        return self.repository.create(match)
