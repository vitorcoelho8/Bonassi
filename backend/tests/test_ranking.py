from __future__ import annotations

import unittest
from datetime import datetime, timezone

from app.bonus.models import BonusAnswer
from app.config import Config
from app.database import db
from app.main import create_app
from app.matches.models import Match
from app.participants.models import Participant
from app.participants.routes import generate_access_token
from app.predictions.models import Prediction
from app.teams.models import Team


class TestConfig(Config):
    TESTING = True
    SECRET_KEY = "test-secret"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False


class RoundRankingTestCase(unittest.TestCase):
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

    def test_round_ranking_returns_empty_state_without_finished_matches(self) -> None:
        response = self.client.get("/api/ranking/round", headers=self.headers)

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIsNone(data["match"])
        self.assertEqual(data["ranking"], [])
        self.assertEqual(data["message"], "Nenhuma partida finalizada ainda.")

    def test_round_ranking_uses_latest_finished_match_only(self) -> None:
        self._create_team("Brasil", "/img/Bandeiras/Brasil.jpg")
        self._create_team("Marrocos", "/img/Bandeiras/Marrocos.jpg")
        self._create_team("Escocia", "/img/Bandeiras/Escocia.jpg")
        maria = self._create_participant("Maria")
        ana = self._create_participant("Ana")
        joao = self._create_participant("Joao")

        older_match = self._create_match(
            home_team="Brasil",
            away_team="Escocia",
            starts_at=datetime(2026, 6, 13, 22, 0, tzinfo=timezone.utc),
            home_score=1,
            away_score=0,
            status="FINISHED",
        )
        latest_match = self._create_match(
            home_team="Brasil",
            away_team="Marrocos",
            starts_at=datetime(2026, 6, 18, 22, 0, tzinfo=timezone.utc),
            home_score=2,
            away_score=1,
            status="finished",
        )
        self._create_prediction(older_match, maria, 1, 0, 8)
        self._create_prediction(latest_match, maria, 2, 1, 8)
        self._create_prediction(latest_match, ana, 1, 0, 6)
        self._create_prediction(latest_match, joao, 1, 0, 6)
        self._create_bonus(maria, 100)
        db.session.commit()

        response = self.client.get("/api/ranking/round", headers=self.headers)

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["match"]["id"], latest_match.id)
        self.assertEqual(data["match"]["home_team"], "Brasil")
        self.assertEqual(data["match"]["away_team"], "Marrocos")
        self.assertEqual(data["match"]["home_score"], 2)
        self.assertEqual(data["match"]["away_score"], 1)
        self.assertEqual(data["match"]["phase"], "GROUP_STAGE")
        self.assertEqual(data["match"]["phase_label"], "Fase de grupos")
        self.assertEqual(data["match"]["home_flag_url"], "/img/Bandeiras/Brasil.jpg")
        self.assertEqual(data["match"]["away_flag_url"], "/img/Bandeiras/Marrocos.jpg")
        self.assertEqual(data["match"]["display_score"], "Brasil 2 x 1 Marrocos")

        self.assertEqual([item["name"] for item in data["ranking"]], ["Maria", "Ana", "Joao"])
        self.assertEqual([item["points"] for item in data["ranking"]], [8, 6, 6])
        self.assertEqual([item["position"] for item in data["ranking"]], [1, 2, 3])
        self.assertTrue(data["ranking"][0]["exact"])
        self.assertFalse(data["ranking"][1]["exact"])
        self.assertEqual(data["ranking"][0]["predicted_score"], "Brasil 2 x 1 Marrocos")
        self.assertEqual(data["ranking"][1]["predicted_score"], "Brasil 1 x 0 Marrocos")

    def test_round_ranking_returns_null_flags_when_team_is_missing(self) -> None:
        participant = self._create_participant("Maria")
        match = self._create_match(
            home_team="Brasil",
            away_team="Marrocos",
            starts_at=datetime(2026, 6, 18, 22, 0, tzinfo=timezone.utc),
            home_score=2,
            away_score=1,
            status="FINISHED",
        )
        self._create_prediction(match, participant, 2, 1, 8)
        db.session.commit()

        response = self.client.get("/api/ranking/round", headers=self.headers)

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIsNone(data["match"]["home_flag_url"])
        self.assertIsNone(data["match"]["away_flag_url"])

    def _create_team(self, name: str, flag_url: str) -> Team:
        team = Team(
            name=name,
            normalized_name=name.lower(),
            flag_url=flag_url,
            is_active=True,
            is_confirmed=True,
        )
        db.session.add(team)
        return team

    def _create_participant(self, name: str) -> Participant:
        participant = Participant(
            name=name,
            email=f"{name.lower()}@test.local",
            role="participant",
            is_active=True,
        )
        db.session.add(participant)
        return participant

    def _create_match(
        self,
        home_team: str,
        away_team: str,
        starts_at: datetime,
        home_score: int,
        away_score: int,
        status: str,
    ) -> Match:
        match = Match(
            home_team=home_team,
            away_team=away_team,
            starts_at=starts_at,
            home_score=home_score,
            away_score=away_score,
            status=status,
            phase="GROUP_STAGE",
            is_brazil_match=True,
            is_active=True,
        )
        db.session.add(match)
        return match

    def _create_prediction(
        self,
        match: Match,
        participant: Participant,
        home_score: int,
        away_score: int,
        points: int,
    ) -> Prediction:
        prediction = Prediction(
            match=match,
            participant=participant,
            home_score=home_score,
            away_score=away_score,
            points=points,
        )
        db.session.add(prediction)
        return prediction

    def _create_bonus(self, participant: Participant, points: int) -> BonusAnswer:
        bonus = BonusAnswer(
            participant=participant,
            question_key="test_bonus",
            answer="ok",
            bonus_type="test",
            status="APPROVED",
            points=points,
        )
        db.session.add(bonus)
        return bonus


if __name__ == "__main__":
    unittest.main()
