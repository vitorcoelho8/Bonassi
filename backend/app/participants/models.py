from uuid import uuid4

from app.database import TimestampMixin, db


class Participant(TimestampMixin, db.Model):
    __tablename__ = "participants"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(30), nullable=False, default="participant")
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    predictions = db.relationship("Prediction", back_populates="participant", lazy=True)
    bonus_answers = db.relationship("BonusAnswer", back_populates="participant", lazy=True)

    def to_dict(self) -> dict[str, str | bool]:
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "is_active": self.is_active,
        }
