from uuid import uuid4

from app.database import TimestampMixin, db


class Prediction(TimestampMixin, db.Model):
    __tablename__ = "predictions"
    __table_args__ = (
        db.UniqueConstraint("participant_id", "match_id", name="uq_prediction_participant_match"),
    )

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    participant_id = db.Column(db.String(36), db.ForeignKey("participants.id"), nullable=False)
    match_id = db.Column(db.String(36), db.ForeignKey("matches.id"), nullable=False)
    home_score = db.Column(db.Integer, nullable=False)
    away_score = db.Column(db.Integer, nullable=False)
    points = db.Column(db.Integer, nullable=False, default=0)

    participant = db.relationship("Participant", back_populates="predictions")
    match = db.relationship("Match", back_populates="predictions")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "participant_id": self.participant_id,
            "match_id": self.match_id,
            "home_score": self.home_score,
            "away_score": self.away_score,
            "predicted_home_score": self.home_score,
            "predicted_away_score": self.away_score,
            "points": self.points,
        }
