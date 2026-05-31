from os import getenv


class Config:
    SECRET_KEY = getenv("SECRET_KEY", "change-me")
    SQLALCHEMY_DATABASE_URI = getenv(
        "DATABASE_URL",
        "postgresql+psycopg://postgres:postgres@localhost:5432/bolao",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS = False
