from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone
from contextlib import redirect_stdout
from io import StringIO

from app.config import Config
from app.database import db
from app.main import create_app
from app.matches.models import Match
from app.participants.models import Participant
from app.participants.routes import generate_access_token
from app.teams.models import Team
from seed_teams import TEAMS, seed_teams

# Import relationship targets before db.create_all().
from app.bonus import models as _bonus_models  # noqa: F401
from app.predictions import models as _prediction_models  # noqa: F401


class TestConfig(Config):
    TESTING = True
    SECRET_KEY = "test-secret"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False


class TeamsTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_app(TestConfig)
        self.context = self.app.app_context()
        self.context.push()
        db.create_all()

        self.admin = Participant(
            name="Admin",
            email="admin@test.local",
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

    def run_seed(self) -> None:
        with redirect_stdout(StringIO()):
            seed_teams()

    def test_seed_teams_is_idempotent(self) -> None:
        self.run_seed()
        self.run_seed()

        self.assertEqual(Team.query.count(), len(TEAMS))
        self.assertEqual(Team.query.filter_by(normalized_name="brasil").count(), 1)
        self.assertTrue(all(team.flag_url for team in Team.query.all()))

    def test_list_teams_returns_catalog(self) -> None:
        self.run_seed()

        response = self.client.get("/api/teams", headers=self.headers)

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), len(TEAMS))
        self.assertIn("flag_url", data[0])

    def test_active_teams_excludes_brazil_inactive_and_unconfirmed(self) -> None:
        self.run_seed()
        morocco = Team.query.filter_by(normalized_name="marrocos").one()
        haiti = Team.query.filter_by(normalized_name="haiti").one()
        morocco.is_active = False
        haiti.is_confirmed = False
        db.session.commit()

        response = self.client.get("/api/teams/active", headers=self.headers)

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        names = {team["name"] for team in data}
        flag_urls = {team["flag_url"] for team in data}
        self.assertNotIn("Brasil", names)
        self.assertNotIn("Marrocos", names)
        self.assertNotIn("Haiti", names)
        self.assertIn("/img/Bandeiras/Escocia.jpg", flag_urls)
        self.assertEqual([team["name"] for team in data], sorted(team["name"] for team in data))

    def test_create_next_brazil_match_accepts_opponent_team_id(self) -> None:
        self.run_seed()
        opponent = Team.query.filter_by(normalized_name="marrocos").one()

        response = self.client.post(
            "/api/admin/matches/next-brazil-match",
            json={
                "phase": "ROUND_OF_32",
                "opponent_team_id": opponent.id,
                "starts_at": (datetime.now(timezone.utc) + timedelta(days=10)).isoformat(),
                "brazil_side": "AWAY",
            },
            headers=self.headers,
        )

        self.assertEqual(response.status_code, 201)
        match = Match.query.one()
        self.assertEqual(match.home_team, "Marrocos")
        self.assertEqual(match.away_team, "Brasil")

    def test_create_next_brazil_match_rejects_unknown_team(self) -> None:
        response = self.client.post(
            "/api/admin/matches/next-brazil-match",
            json={
                "phase": "ROUND_OF_32",
                "opponent_team_id": 999,
                "starts_at": (datetime.now(timezone.utc) + timedelta(days=10)).isoformat(),
                "brazil_side": "HOME",
            },
            headers=self.headers,
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"], "Seleção adversária não encontrada.")

    def test_create_next_brazil_match_rejects_brazil_as_opponent(self) -> None:
        self.run_seed()
        brazil = Team.query.filter_by(normalized_name="brasil").one()

        response = self.client.post(
            "/api/admin/matches/next-brazil-match",
            json={
                "phase": "ROUND_OF_32",
                "opponent_team_id": brazil.id,
                "starts_at": (datetime.now(timezone.utc) + timedelta(days=10)).isoformat(),
                "brazil_side": "HOME",
            },
            headers=self.headers,
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"], "Brasil não pode ser selecionado como adversário.")

    def test_create_next_brazil_match_rejects_inactive_team(self) -> None:
        self.run_seed()
        opponent = Team.query.filter_by(normalized_name="marrocos").one()
        opponent.is_active = False
        db.session.commit()

        response = self.client.post(
            "/api/admin/matches/next-brazil-match",
            json={
                "phase": "ROUND_OF_32",
                "opponent_team_id": opponent.id,
                "starts_at": (datetime.now(timezone.utc) + timedelta(days=10)).isoformat(),
                "brazil_side": "HOME",
            },
            headers=self.headers,
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"], "A seleção adversária não está ativa.")


if __name__ == "__main__":
    unittest.main()
