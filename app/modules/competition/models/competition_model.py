from uuid import uuid4

from app.database.base_model import TimestampMixin
from app.database.extensions import db


class Competition(TimestampMixin, db.Model):
    __tablename__ = "competitions"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    name = db.Column(db.String(120), nullable=False)
    season = db.Column(db.String(20), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    def to_dict(self) -> dict[str, str | bool]:
        return {
            "id": self.id,
            "name": self.name,
            "season": self.season,
            "is_active": self.is_active,
        }
