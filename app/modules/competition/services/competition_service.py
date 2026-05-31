from app.modules.competition.models.competition_model import Competition
from app.modules.competition.repositories.competition_repository import (
    CompetitionRepository,
)


class CompetitionService:
    def __init__(
        self,
        competition_repository: CompetitionRepository | None = None,
    ) -> None:
        self.competition_repository = competition_repository or CompetitionRepository()

    def list_active(self) -> list[Competition]:
        return self.competition_repository.list_active()

    def create(self, data: dict) -> Competition:
        competition = Competition(name=data["name"], season=data["season"])
        return self.competition_repository.create(competition)
