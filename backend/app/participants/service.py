from werkzeug.security import check_password_hash, generate_password_hash

from app.database import db
from app.participants.models import Participant


class ParticipantRepository:
    def list_active(self) -> list[Participant]:
        return Participant.query.filter_by(is_active=True).order_by(Participant.name).all()

    def get_by_email(self, email: str) -> Participant | None:
        return Participant.query.filter_by(email=email).first()

    def get_by_id(self, participant_id: str) -> Participant | None:
        return db.session.get(Participant, participant_id)

    def create(self, participant: Participant) -> Participant:
        db.session.add(participant)
        db.session.commit()
        return participant


class ParticipantService:
    def __init__(self, repository: ParticipantRepository | None = None) -> None:
        self.repository = repository or ParticipantRepository()

    def list_active(self) -> list[Participant]:
        return self.repository.list_active()

    def get_by_id(self, participant_id: str) -> Participant | None:
        return self.repository.get_by_id(participant_id)

    def register(self, data: dict, role: str = "participant") -> Participant:
        if self.repository.get_by_email(data["email"]):
            raise ValueError("Email already registered.")

        participant = Participant(
            name=data["name"],
            email=data["email"],
            password_hash=generate_password_hash(data["password"]),
            role=role,
        )
        return self.repository.create(participant)

    def authenticate(self, email: str, password: str) -> Participant:
        participant = self.repository.get_by_email(email)

        if not participant or not check_password_hash(participant.password_hash, password):
            raise ValueError("Invalid credentials.")

        if not participant.is_active:
            raise ValueError("Inactive participant.")

        return participant
