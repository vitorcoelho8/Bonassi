from uuid import uuid4

from app.database import TimestampMixin, db


class Match(TimestampMixin, db.Model):
    __tablename__ = "matches"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    home_team = db.Column(db.String(80), nullable=False)
    away_team = db.Column(db.String(80), nullable=False)
    starts_at = db.Column(db.DateTime(timezone=True), nullable=True)
    home_score = db.Column(db.Integer, nullable=True)
    away_score = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(30), nullable=False, default="scheduled")
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    predictions = db.relationship("Prediction", back_populates="match", lazy=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "home_team": self.home_team,
            "away_team": self.away_team,
            "starts_at": self.starts_at.isoformat() if self.starts_at else None,
            "home_score": self.home_score,
            "away_score": self.away_score,
            "status": self.status,
            "is_active": self.is_active,
        }
