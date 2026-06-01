from datetime import datetime, timezone

from flask import current_app
from sqlalchemy import func
from werkzeug.security import generate_password_hash

from app.database import db
from app.matches.models import Match
from app.matches.phases import MATCH_PHASES, is_knockout_phase, normalize_phase, phase_round_order
from app.participants.models import Participant
from app.participants.service import ParticipantService
from app.predictions.models import Prediction
from app.predictions.service import calculate_match_points


DEFAULT_ADMIN_EMAIL = "admin@bonassi.com"
DEFAULT_ADMIN_NAME = "Administrador"
DEFAULT_ADMIN_PASSWORD = "123456a!"
ADMIN_NEXT_MATCH_PHASES = (
    "ROUND_OF_32",
    "ROUND_OF_16",
    "QUARTER_FINAL",
    "SEMI_FINAL",
    "FINAL",
    "THIRD_PLACE",
)


def ensure_default_admin() -> None:
    admin_email = current_app.config.get("ADMIN_EMAIL") or DEFAULT_ADMIN_EMAIL
    admin_name = current_app.config.get("ADMIN_NAME") or DEFAULT_ADMIN_NAME
    configured_password = current_app.config.get("ADMIN_PASSWORD")
    is_production = current_app.config.get("SESSION_COOKIE_SECURE", False)

    if is_production and not configured_password:
        raise RuntimeError("ADMIN_PASSWORD must be configured before creating the initial admin.")

    admin = Participant.query.filter_by(email=admin_email).first()
    password = configured_password or DEFAULT_ADMIN_PASSWORD

    if admin is None:
        admin = Participant(
            name=admin_name,
            email=admin_email,
            password_hash=generate_password_hash(password),
            role="admin",
            is_active=True,
        )
        db.session.add(admin)
    else:
        admin.name = admin_name
        if configured_password or not admin.password_hash:
            admin.password_hash = generate_password_hash(password)
        admin.role = "admin"
        admin.is_active = True

    db.session.commit()


class AdminService:
    def list_participants(self) -> list[Participant]:
        return ParticipantService().list_active()

    def list_next_match_phases(self) -> list[dict]:
        return [
            {
                "value": phase,
                "label": MATCH_PHASES[phase]["label"],
                "round_order": MATCH_PHASES[phase]["round_order"],
            }
            for phase in ADMIN_NEXT_MATCH_PHASES
            if phase in MATCH_PHASES
        ]

    def create_next_brazil_match(self, data: dict) -> Match:
        phase = self._parse_next_match_phase(data)
        opponent_team = self._parse_opponent_team(data)
        starts_at = self._parse_starts_at(data)
        brazil_side = self._parse_brazil_side(data)

        if self._has_brazil_match_for_phase(phase):
            raise ValueError("Ja existe uma partida do Brasil cadastrada para esta fase.")

        if self._has_future_scheduled_brazil_match():
            raise ValueError("Ja existe uma partida futura do Brasil disponivel para palpites.")

        if brazil_side == "HOME":
            home_team = "Brasil"
            away_team = opponent_team
        else:
            home_team = opponent_team
            away_team = "Brasil"

        match = Match(
            home_team=home_team,
            away_team=away_team,
            starts_at=starts_at,
            home_score=None,
            away_score=None,
            status="SCHEDULED",
            phase=phase,
            round_order=phase_round_order(phase),
            is_brazil_match=True,
            is_knockout=is_knockout_phase(phase),
            created_manually_by_admin=True,
            is_active=True,
        )
        db.session.add(match)
        db.session.commit()
        return match

    def save_match_result(self, match_id: str, data: dict) -> tuple[Match, int]:
        match = db.session.get(Match, match_id)
        if match is None:
            raise ValueError("Jogo nao encontrado.")

        home_score = self._parse_score(data, "home_score")
        away_score = self._parse_score(data, "away_score")

        match.home_score = home_score
        match.away_score = away_score
        match.status = "FINISHED"

        predictions = Prediction.query.filter_by(match_id=match.id).all()
        for prediction in predictions:
            prediction.points = calculate_match_points(
                prediction.home_score,
                prediction.away_score,
                home_score,
                away_score,
            )

        db.session.commit()
        return match, len(predictions)

    def _parse_score(self, data: dict, field: str) -> int:
        if field not in data or data[field] in (None, ""):
            raise ValueError("home_score e away_score sao obrigatorios.")

        value = data[field]
        if isinstance(value, bool):
            raise ValueError("home_score e away_score devem ser numeros inteiros.")

        if isinstance(value, int):
            score = value
        elif isinstance(value, str) and value.strip().isdigit():
            score = int(value.strip())
        else:
            raise ValueError("home_score e away_score devem ser numeros inteiros.")

        if score < 0:
            raise ValueError("home_score e away_score devem ser maiores ou iguais a zero.")

        return score

    def _parse_next_match_phase(self, data: dict) -> str:
        if not data.get("phase"):
            raise ValueError("phase e obrigatorio.")

        phase = normalize_phase(data.get("phase"))
        if phase not in ADMIN_NEXT_MATCH_PHASES:
            raise ValueError("Fase da partida invalida.")

        return phase

    def _parse_opponent_team(self, data: dict) -> str:
        if not data.get("opponent_team"):
            raise ValueError("opponent_team e obrigatorio.")

        opponent_team = str(data["opponent_team"]).strip()
        if not opponent_team:
            raise ValueError("opponent_team e obrigatorio.")

        if opponent_team.lower() == "brasil":
            raise ValueError("O adversario nao pode ser Brasil.")

        return opponent_team

    def _parse_starts_at(self, data: dict) -> datetime:
        if not data.get("starts_at"):
            raise ValueError("starts_at e obrigatorio.")

        try:
            starts_at = datetime.fromisoformat(str(data["starts_at"]).replace("Z", "+00:00"))
        except ValueError as error:
            raise ValueError("starts_at deve ser uma data e hora validas.") from error

        if starts_at.tzinfo is None:
            raise ValueError("starts_at deve incluir timezone.")

        if starts_at <= datetime.now(timezone.utc):
            raise ValueError("starts_at deve representar uma data futura.")

        return starts_at

    def _parse_brazil_side(self, data: dict) -> str:
        if not data.get("brazil_side"):
            raise ValueError("brazil_side e obrigatorio.")

        brazil_side = str(data["brazil_side"]).strip().upper()
        if brazil_side not in {"HOME", "AWAY"}:
            raise ValueError("brazil_side deve ser HOME ou AWAY.")

        return brazil_side

    def _has_brazil_match_for_phase(self, phase: str) -> bool:
        return (
            Match.query.filter(Match.is_brazil_match.is_(True))
            .filter(func.upper(Match.phase) == phase)
            .filter(func.upper(Match.status) != "CANCELLED")
            .first()
            is not None
        )

    def _has_future_scheduled_brazil_match(self) -> bool:
        return (
            Match.query.filter(Match.is_brazil_match.is_(True))
            .filter(Match.starts_at.isnot(None))
            .filter(Match.starts_at > datetime.now(timezone.utc))
            .filter(func.upper(Match.status) == "SCHEDULED")
            .first()
            is not None
        )
