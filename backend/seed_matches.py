from __future__ import annotations

from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError


BACKEND_DIR = Path(__file__).resolve().parent
load_dotenv(BACKEND_DIR / ".env")

from app.database import db
from app.main import create_app
from app.matches.models import Match


SAO_PAULO_TZ = ZoneInfo("America/Sao_Paulo")


MATCHES = (
    {
        "home_team": "Brasil",
        "away_team": "Marrocos",
        "starts_at": datetime(2026, 6, 13, 19, 0, tzinfo=SAO_PAULO_TZ),
    },
    {
        "home_team": "Brasil",
        "away_team": "Haiti",
        "starts_at": datetime(2026, 6, 19, 21, 30, tzinfo=SAO_PAULO_TZ),
    },
    {
        "home_team": "Escócia",
        "away_team": "Brasil",
        "starts_at": datetime(2026, 6, 24, 19, 0, tzinfo=SAO_PAULO_TZ),
    },
)


def find_existing_match(match_data: dict) -> Match | None:
    stmt = select(Match).where(
        Match.home_team == match_data["home_team"],
        Match.away_team == match_data["away_team"],
        Match.starts_at == match_data["starts_at"],
    )
    return db.session.execute(stmt).scalar_one_or_none()


def format_match(match_data: dict) -> str:
    starts_at = match_data["starts_at"].astimezone(SAO_PAULO_TZ)
    return (
        f"{match_data['home_team']} x {match_data['away_team']} - "
        f"{starts_at:%d/%m/%Y %H:%M}"
    )


def seed_matches() -> None:
    print("Inserindo jogos da primeira fase...")

    for match_data in MATCHES:
        if find_existing_match(match_data):
            print(f"[=] Jogo já existe: {match_data['home_team']} x {match_data['away_team']}")
            continue

        db.session.add(
            Match(
                home_team=match_data["home_team"],
                away_team=match_data["away_team"],
                starts_at=match_data["starts_at"],
                status="SCHEDULED",
                is_active=True,
            )
        )
        print(f"[+] Criado: {format_match(match_data)}")

    db.session.commit()
    print("Seed concluído com sucesso!")


def main() -> None:
    app = create_app()
    with app.app_context():
        try:
            seed_matches()
        except SQLAlchemyError as error:
            db.session.rollback()
            print(f"Erro ao executar seed: {error}")
            raise SystemExit(1) from error


if __name__ == "__main__":
    main()
