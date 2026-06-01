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
    admin = Participant.query.filter_by(email=DEFAULT_ADMIN_EMAIL).first()
    password_hash = generate_password_hash(DEFAULT_ADMIN_PASSWORD)

    if admin is None:
        admin = Participant(
            name=DEFAULT_ADMIN_NAME,
            email=DEFAULT_ADMIN_EMAIL,
            password_hash=password_hash,
            role="admin",
            is_active=True,
        )
        db.session.add(admin)
    else:
        admin.name = DEFAULT_ADMIN_NAME
        admin.password_hash = password_hash
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
