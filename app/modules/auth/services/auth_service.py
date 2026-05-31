from werkzeug.security import check_password_hash, generate_password_hash

from app.modules.auth.models.user_model import User
from app.modules.auth.repositories.user_repository import UserRepository


class AuthService:
    def __init__(self, user_repository: UserRepository | None = None) -> None:
        self.user_repository = user_repository or UserRepository()

    def register(self, data: dict) -> User:
        existing_user = self.user_repository.get_by_email(data["email"])
        if existing_user:
            raise ValueError("Email already registered.")

        user = User(
            name=data["name"],
            email=data["email"],
            password_hash=generate_password_hash(data["password"]),
        )
        return self.user_repository.create(user)

    def authenticate(self, email: str, password: str) -> User:
        user = self.user_repository.get_by_email(email)

        if not user or not check_password_hash(user.password_hash, password):
            raise ValueError("Invalid credentials.")

        if not user.is_active:
            raise ValueError("Inactive user.")

        return user
