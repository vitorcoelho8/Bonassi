from __future__ import annotations

import unittest
from datetime import datetime, timezone

from app.config import Config
from app.database import db
from app.main import create_app
from app.matches.models import Match
from app.participants.models import Participant
from app.participants.routes import generate_access_token
from app.predictions.models import Prediction
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

    def test_update_match_changes_scheduled_match(self) -> None:
        brazil, morocco, france = self._create_basic_teams()
        match = self._create_match("Brasil", "Marrocos")
        db.session.commit()

        response = self.client.put(
            f"/api/admin/matches/{match.id}",
            json={
                "phase": "ROUND_OF_16",
                "opponent_team_id": france.id,
                "starts_at": "2026-07-01T16:00:00-03:00",
                "brazil_side": "AWAY",
            },
            headers=self.headers,
        )

        self.assertEqual(response.status_code, 200)
        db.session.refresh(match)
        self.assertEqual(match.home_team, "Franca")
        self.assertEqual(match.away_team, "Brasil")
        self.assertEqual(match.phase, "ROUND_OF_16")
        self.assertTrue(match.is_brazil_match)
        self.assertTrue(match.is_knockout)
        data = response.get_json()
        self.assertEqual(data["message"], "Partida atualizada com sucesso.")
        self.assertEqual(data["match"]["home_flag_url"], "/img/Bandeiras/Franca.jpg")
        self.assertEqual(brazil.name, "Brasil")
        self.assertEqual(morocco.name, "Marrocos")

    def test_update_match_rejects_unknown_opponent(self) -> None:
        self._create_basic_teams()
        match = self._create_match("Brasil", "Marrocos")
        db.session.commit()

        response = self.client.put(
            f"/api/admin/matches/{match.id}",
            json={
                "phase": "GROUP_STAGE",
                "opponent_team_id": 999,
                "starts_at": "2026-06-20T16:00:00-03:00",
                "brazil_side": "HOME",
            },
            headers=self.headers,
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("advers", response.get_json()["error"].lower())

    def test_update_match_rejects_brazil_as_opponent(self) -> None:
        brazil, _, _ = self._create_basic_teams()
        match = self._create_match("Brasil", "Marrocos")
        db.session.commit()

        response = self.client.put(
            f"/api/admin/matches/{match.id}",
            json={
                "phase": "GROUP_STAGE",
                "opponent_team_id": brazil.id,
                "starts_at": "2026-06-20T16:00:00-03:00",
                "brazil_side": "HOME",
            },
            headers=self.headers,
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("Brasil", response.get_json()["error"])

    def test_update_match_rejects_finished_match(self) -> None:
        _, _, france = self._create_basic_teams()
        match = self._create_match("Brasil", "Marrocos", status="FINISHED", home_score=2, away_score=1)
        db.session.commit()

        response = self.client.put(
            f"/api/admin/matches/{match.id}",
            json={
                "phase": "ROUND_OF_16",
                "opponent_team_id": france.id,
                "starts_at": "2026-07-01T16:00:00-03:00",
                "brazil_side": "AWAY",
            },
            headers=self.headers,
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.get_json()["error"],
            "Nao e possivel editar uma partida finalizada. Reabra a partida ou edite apenas o resultado.",
        )

    def test_delete_match_without_predictions_or_result_removes_match(self) -> None:
        self._create_basic_teams()
        match = self._create_match("Brasil", "Marrocos")
        db.session.commit()
        match_id = match.id

        response = self.client.delete(f"/api/admin/matches/{match_id}", headers=self.headers)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["message"], "Partida excluida com sucesso.")
        self.assertIsNone(db.session.get(Match, match_id))

    def test_delete_match_with_predictions_cancels_match(self) -> None:
        self._create_basic_teams()
        participant = Participant(name="Maria", email="maria@test.local", role="participant", is_active=True)
        match = self._create_match("Brasil", "Marrocos")
        db.session.add(participant)
        db.session.flush()
        db.session.add(Prediction(match=match, participant=participant, home_score=2, away_score=1, points=0))
        db.session.commit()

        response = self.client.delete(f"/api/admin/matches/{match.id}", headers=self.headers)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json()["message"],
            "Partida cancelada com sucesso. Os registros historicos foram preservados.",
        )
        db.session.refresh(match)
        self.assertEqual(match.status, "CANCELLED")

    def test_next_match_ignores_cancelled_matches(self) -> None:
        self._create_basic_teams()
        self._create_match("Brasil", "Marrocos", status="CANCELLED")
        db.session.commit()

        response = self.client.get("/api/matches/next", headers=self.headers)

        self.assertEqual(response.status_code, 404)

    def _create_basic_teams(self) -> tuple[Team, Team, Team]:
        brazil = Team(
            name="Brasil",
            normalized_name="brasil",
            flag_url="/img/Bandeiras/Brasil.jpg",
            is_brazil=True,
        )
        morocco = Team(
            name="Marrocos",
            normalized_name="marrocos",
            flag_url="/img/Bandeiras/Marrocos.jpg",
        )
        france = Team(
            name="Franca",
            normalized_name="franca",
            flag_url="/img/Bandeiras/Franca.jpg",
        )
        db.session.add_all([brazil, morocco, france])
        return brazil, morocco, france

    def _create_match(
        self,
        home_team: str,
        away_team: str,
        status: str = "SCHEDULED",
        home_score: int | None = None,
        away_score: int | None = None,
    ) -> Match:
        match = Match(
            home_team=home_team,
            away_team=away_team,
            starts_at=datetime(2026, 6, 20, 22, 0, tzinfo=timezone.utc),
            home_score=home_score,
            away_score=away_score,
            status=status,
            phase="GROUP_STAGE",
            is_brazil_match=True,
            is_active=True,
        )
        db.session.add(match)
        return match


if __name__ == "__main__":
    unittest.main()
