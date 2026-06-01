from uuid import uuid4

from app.database import TimestampMixin, db
from app.matches.phases import phase_label


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
    phase = db.Column(db.String(40), nullable=True)
    round_order = db.Column(db.Integer, nullable=True)
    is_brazil_match = db.Column(db.Boolean, nullable=False, default=True)
    is_knockout = db.Column(db.Boolean, nullable=False, default=False)
    created_manually_by_admin = db.Column(db.Boolean, nullable=False, default=False)

    predictions = db.relationship("Prediction", back_populates="match", lazy=True)

    def to_dict(self) -> dict:
        starts_at = self.starts_at.isoformat() if self.starts_at else None
        return {
            "id": self.id,
            "home_team": self.home_team,
            "away_team": self.away_team,
            "starts_at": starts_at,
            "match_date": starts_at,
            "home_score": self.home_score,
            "away_score": self.away_score,
            "status": self.status.upper() if self.status else self.status,
            "is_active": self.is_active,
            "phase": self.phase,
            "phase_label": phase_label(self.phase),
            "round_order": self.round_order,
            "is_brazil_match": self.is_brazil_match,
            "is_knockout": self.is_knockout,
            "created_manually_by_admin": self.created_manually_by_admin,
        }
