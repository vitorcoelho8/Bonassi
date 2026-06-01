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
from app.teams.models import Team


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
        brazil_side = self._parse_brazil_side(data)
        starts_at = self._parse_starts_at(data)

        if self._has_brazil_match_for_phase(phase):
            raise ValueError("Ja existe uma partida do Brasil cadastrada para esta fase.")

        if self._has_future_scheduled_brazil_match():
            raise ValueError("Ja existe uma partida futura do Brasil disponivel para palpites.")

        match = Match(
            home_team="Brasil" if brazil_side == "HOME" else opponent_team,
            away_team=opponent_team if brazil_side == "HOME" else "Brasil",
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

    def update_match(self, match_id: str, data: dict) -> Match:
        match = db.session.get(Match, match_id)
        if match is None:
            raise ValueError("Partida nao encontrada.")

        status = str(match.status or "").upper()
        if status == "FINISHED":
            raise ValueError("Nao e possivel editar uma partida finalizada. Reabra a partida ou edite apenas o resultado.")

        if status != "SCHEDULED":
            raise ValueError("Apenas partidas agendadas podem ser editadas.")

        phase = self._parse_match_phase(data)
        opponent_team = self._parse_opponent_team(data)
        brazil_side = self._parse_brazil_side(data)
        starts_at = self._parse_starts_at(data)

        match.home_team = "Brasil" if brazil_side == "HOME" else opponent_team
        match.away_team = opponent_team if brazil_side == "HOME" else "Brasil"
        match.starts_at = starts_at
        match.phase = phase
        match.round_order = phase_round_order(phase)
        match.is_brazil_match = True
        match.is_knockout = is_knockout_phase(phase)

        db.session.commit()
        return match

    def delete_match(self, match_id: str) -> tuple[Match | None, bool]:
        match = db.session.get(Match, match_id)
        if match is None:
            raise ValueError("Partida nao encontrada.")

        has_predictions = Prediction.query.filter_by(match_id=match.id).first() is not None
        has_result = match.home_score is not None or match.away_score is not None

        if not has_predictions and not has_result:
            db.session.delete(match)
            db.session.commit()
            return None, True

        match.status = "CANCELLED"
        db.session.commit()
        return match, False

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

    def reopen_match(self, match_id: str) -> tuple[Match, bool]:
        match = db.session.get(Match, match_id)
        if match is None:
            raise ValueError("Partida nao encontrada.")

        is_finished = str(match.status or "").upper() == "FINISHED"
        if not is_finished:
            return match, False

        match.status = "SCHEDULED"

        db.session.commit()
        return match, True

    def reset_match_result(self, match_id: str) -> tuple[Match, bool]:
        return self.reopen_match(match_id)

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

        phase = self._parse_match_phase(data)
        if phase not in ADMIN_NEXT_MATCH_PHASES:
            raise ValueError("Fase da partida invalida.")

        return phase

    def _parse_match_phase(self, data: dict) -> str:
        if not data.get("phase"):
            raise ValueError("phase e obrigatorio.")

        return normalize_phase(data.get("phase"))

    def _parse_opponent_team(self, data: dict) -> str:
        opponent_team_id = data.get("opponent_team_id")
        if opponent_team_id not in (None, ""):
            try:
                team_id = int(opponent_team_id)
            except (TypeError, ValueError) as error:
                raise ValueError("Seleção adversária não encontrada.") from error

            team = db.session.get(Team, team_id)
            if team is None:
                raise ValueError("Seleção adversária não encontrada.")

            if team.is_brazil:
                raise ValueError("Brasil não pode ser selecionado como adversário.")

            if not team.is_active:
                raise ValueError("A seleção adversária não está ativa.")

            if not team.is_confirmed:
                raise ValueError("A seleção adversária não está confirmada.")

            return team.name

        if not data.get("opponent_team"):
            raise ValueError("opponent_team e obrigatorio.")

        opponent_team = str(data["opponent_team"]).strip()
        if not opponent_team:
            raise ValueError("opponent_team e obrigatorio.")

        if opponent_team.lower() == "brasil":
            raise ValueError("Brasil não pode ser selecionado como adversário.")

        return opponent_team

    def _parse_brazil_side(self, data: dict) -> str:
        brazil_side = str(data.get("brazil_side") or "HOME").strip().upper()
        if brazil_side not in {"HOME", "AWAY"}:
            raise ValueError("brazil_side deve ser HOME ou AWAY.")

        return brazil_side

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
