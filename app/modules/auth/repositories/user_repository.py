from app.database.extensions import db
from app.modules.auth.models.user_model import User


class UserRepository:
    def get_by_email(self, email: str) -> User | None:
        return User.query.filter_by(email=email).first()

    def get_by_id(self, user_id: str) -> User | None:
        return db.session.get(User, user_id)

    def create(self, user: User) -> User:
        db.session.add(user)
        db.session.commit()
        return user
