from uuid import uuid4

from app.database import TimestampMixin, db


class BonusAnswer(TimestampMixin, db.Model):
    __tablename__ = "bonus_answers"
    __table_args__ = (
        db.UniqueConstraint("participant_id", "question_key", name="uq_bonus_participant_question"),
    )

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    participant_id = db.Column(db.String(36), db.ForeignKey("participants.id"), nullable=False)
    question_key = db.Column(db.String(80), nullable=False)
    answer = db.Column(db.String(255), nullable=False)
    points = db.Column(db.Integer, nullable=False, default=0)

    participant = db.relationship("Participant", back_populates="bonus_answers")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "participant_id": self.participant_id,
            "question_key": self.question_key,
            "answer": self.answer,
            "points": self.points,
        }
