from werkzeug.security import generate_password_hash

from app.database import db
from app.participants.models import Participant
from app.participants.service import ParticipantService


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
