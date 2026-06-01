from flask import current_app
from werkzeug.security import generate_password_hash

from app.database import db
from app.matches.models import Match
from app.participants.models import Participant
from app.participants.service import ParticipantService
from app.predictions.models import Prediction
from app.predictions.service import calculate_match_points


DEFAULT_ADMIN_EMAIL = "admin@bonassi.com"
DEFAULT_ADMIN_NAME = "Administrador"
DEFAULT_ADMIN_PASSWORD = "123456a!"


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
