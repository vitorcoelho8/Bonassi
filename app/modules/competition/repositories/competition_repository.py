from app.database.extensions import db
from app.modules.competition.models.competition_model import Competition


class CompetitionRepository:
    def list_active(self) -> list[Competition]:
        return Competition.query.filter_by(is_active=True).order_by(Competition.name).all()

    def get_by_id(self, competition_id: str) -> Competition | None:
        return db.session.get(Competition, competition_id)

    def create(self, competition: Competition) -> Competition:
        db.session.add(competition)
        db.session.commit()
        return competition
