from datetime import datetime, timezone

from app.database import db


class Team(db.Model):
    __tablename__ = "teams"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    normalized_name = db.Column(db.String(120), nullable=False, unique=True)
    fifa_code = db.Column(db.String(10), nullable=True, unique=True)
    group_name = db.Column(db.String(10), nullable=True)
    flag_url = db.Column(db.String(255), nullable=True)
    is_brazil = db.Column(db.Boolean, nullable=False, default=False)
    is_confirmed = db.Column(db.Boolean, nullable=False, default=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "normalized_name": self.normalized_name,
            "fifa_code": self.fifa_code,
            "group_name": self.group_name,
            "flag_url": self.flag_url,
            "is_brazil": self.is_brazil,
            "is_confirmed": self.is_confirmed,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
