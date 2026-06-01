from os import getenv
from pathlib import Path
from datetime import timedelta


BACKEND_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = BACKEND_DIR.parent


def _is_production() -> bool:
    return (
        getenv("FLASK_ENV", "").lower() == "production"
        or getenv("ENV", "").lower() == "production"
    )


def _secret_key() -> str:
    secret = getenv("SECRET_KEY", "change-me")

    if _is_production() and secret in {"change-me", "change-this-secret"}:
        raise RuntimeError("SECRET_KEY must be configured with a strong value in production.")

    return secret


def _database_url() -> str:
    database_url = getenv("DATABASE_URL")

    if not database_url:
        if _is_production():
            raise RuntimeError("DATABASE_URL must be configured in production.")

        return "postgresql+psycopg://postgres:postgres@localhost:5432/bolao"

    if database_url.startswith("postgresql://"):
        database_url = database_url.replace(
            "postgresql://",
            "postgresql+psycopg://",
            1
        )

    if database_url.startswith("postgres://"):
        database_url = database_url.replace(
            "postgres://",
            "postgresql+psycopg://",
            1
        )

    return database_url


class Config:
    IS_PRODUCTION = _is_production()
    SECRET_KEY = _secret_key()
    SQLALCHEMY_DATABASE_URI = _database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS = False

    FRONTEND_DIR = Path(getenv("FRONTEND_DIR", PROJECT_DIR / "frontend")).resolve()

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = IS_PRODUCTION
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)

    AUTH_TOKEN_SALT = getenv("AUTH_TOKEN_SALT", "bonassi-auth-token")
    AUTH_TOKEN_MAX_AGE_SECONDS = int(getenv("AUTH_TOKEN_MAX_AGE_SECONDS", str(8 * 60 * 60)))

    ADMIN_EMAIL = getenv("ADMIN_EMAIL", "admin@bonassi.com")
    ADMIN_NAME = getenv("ADMIN_NAME", "Administrador")
    ADMIN_PASSWORD = getenv("ADMIN_PASSWORD")
