from __future__ import annotations

import unittest
from datetime import datetime, timezone

from app.config import Config
from app.database import db
from app.main import create_app
from app.matches.models import Match
from app.participants.models import Participant
from app.participants.routes import generate_access_token
from app.teams.models import Team

# Import relationship targets before db.create_all().
from app.bonus import models as _bonus_models  # noqa: F401
from app.predictions import models as _prediction_models  # noqa: F401


class TestConfig(Config):
    TESTING = True
    SECRET_KEY = "test-secret"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False


class MatchesTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_app(TestConfig)
        self.context = self.app.app_context()
        self.context.push()
        db.create_all()

        self.admin = Participant(
            name="Admin",
            email="admin-matches@test.local",
            role="admin",
            is_active=True,
        )
        db.session.add(self.admin)
        db.session.commit()

        token = generate_access_token(self.admin.id)
        self.headers = {"Authorization": f"Bearer {token}"}
        self.client = self.app.test_client()

    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()
        self.context.pop()

    def test_list_matches_returns_team_flags(self) -> None:
        db.session.add_all([
            Team(
                name="Brasil",
                normalized_name="brasil",
                flag_url="/img/Bandeiras/Brasil.jpg",
                is_brazil=True,
            ),
            Team(
                name="Marrocos",
                normalized_name="marrocos",
                flag_url="/img/Bandeiras/Marrocos.jpg",
            ),
            Match(
                home_team="Brasil",
                away_team="Marrocos",
                starts_at=datetime(2026, 6, 13, 22, 0, tzinfo=timezone.utc),
                status="SCHEDULED",
                phase="GROUP_STAGE",
                is_brazil_match=True,
                is_active=True,
            ),
        ])
        db.session.commit()

        response = self.client.get("/api/matches", headers=self.headers)

        self.assertEqual(response.status_code, 200)
        match = response.get_json()["items"][0]
        self.assertEqual(match["home_flag_url"], "/img/Bandeiras/Brasil.jpg")
        self.assertEqual(match["away_flag_url"], "/img/Bandeiras/Marrocos.jpg")

    def test_list_matches_resolves_flags_by_normalized_team_name(self) -> None:
        db.session.add_all([
            Team(
                name="Escócia",
                normalized_name="escocia",
                flag_url="/img/Bandeiras/Escocia.jpg",
            ),
            Team(
                name="Brasil",
                normalized_name="brasil",
                flag_url="/img/Bandeiras/Brasil.jpg",
                is_brazil=True,
            ),
            Match(
                home_team="Escocia",
                away_team="Brasil",
                starts_at=datetime(2026, 6, 20, 22, 0, tzinfo=timezone.utc),
                status="SCHEDULED",
                phase="GROUP_STAGE",
                is_brazil_match=True,
                is_active=True,
            ),
        ])
        db.session.commit()

        response = self.client.get("/api/matches", headers=self.headers)

        self.assertEqual(response.status_code, 200)
        match = response.get_json()["items"][0]
        self.assertEqual(match["home_flag_url"], "/img/Bandeiras/Escocia.jpg")
        self.assertEqual(match["away_flag_url"], "/img/Bandeiras/Brasil.jpg")


if __name__ == "__main__":
    unittest.main()
