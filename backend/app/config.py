from os import getenv
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = BACKEND_DIR.parent


class Config:
    SECRET_KEY = getenv("SECRET_KEY", "change-me")
    SQLALCHEMY_DATABASE_URI = getenv(
        "DATABASE_URL",
        "postgresql+psycopg://postgres:postgres@localhost:5432/bolao",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS = False
    FRONTEND_DIR = Path(getenv("FRONTEND_DIR", PROJECT_DIR / "frontend")).resolve()
