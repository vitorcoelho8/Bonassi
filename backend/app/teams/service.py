from app.teams.models import Team


class TeamService:
    def list_all(self) -> list[Team]:
        return Team.query.order_by(Team.name.asc()).all()

    def list_active_opponents(self) -> list[Team]:
        return (
            Team.query.filter(Team.is_active.is_(True))
            .filter(Team.is_confirmed.is_(True))
            .filter(Team.is_brazil.is_(False))
            .order_by(Team.name.asc())
            .all()
        )
