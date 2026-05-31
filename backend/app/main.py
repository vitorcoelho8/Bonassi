from pathlib import Path

from flask import Flask, jsonify, redirect, send_from_directory, session, url_for
from flask.cli import with_appcontext

from app.admin.routes import admin_bp
from app.admin.service import ensure_default_admin
from app.bonus.routes import bonus_bp
from app.config import Config
from app.database import db, migrate
from app.matches.routes import matches_bp
from app.participants.routes import participants_bp
from app.participants.service import ParticipantService
from app.predictions.routes import predictions_bp
from app.ranking.routes import ranking_bp


def create_app(config_class: type[Config] = Config) -> Flask:
    app = Flask(__name__, static_folder=None)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db, directory="alembic")
    register_commands(app)
    register_blueprints(app)
    register_frontend_routes(app)

    return app


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(participants_bp, url_prefix="/api/participants")
    app.register_blueprint(participants_bp, url_prefix="/api/auth", name="auth")
    app.register_blueprint(matches_bp, url_prefix="/api/matches")
    app.register_blueprint(predictions_bp, url_prefix="/api/predictions")
    app.register_blueprint(bonus_bp, url_prefix="/api/bonus")
    app.register_blueprint(ranking_bp, url_prefix="/api/ranking")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")


def register_frontend_routes(app: Flask) -> None:
    frontend_dir = Path(app.config["FRONTEND_DIR"])

    @app.get("/api/health")
    def health_check() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/")
    def index():
        if _is_authenticated():
            return redirect(url_for("frontend_page", filename="ranking.html"))

        return send_from_directory(frontend_dir, "index.html")

    @app.get("/home")
    def home_page():
        return redirect(url_for("frontend_page", filename="ranking.html"))

    @app.get("/login")
    def login_page():
        return send_from_directory(frontend_dir, "index.html")

    @app.get("/<path:filename>")
    def frontend_page(filename: str):
        return send_from_directory(frontend_dir, filename)


def register_commands(app: Flask) -> None:
    @app.cli.command("init-db")
    @with_appcontext
    def init_db_command() -> None:
        db.create_all()
        ensure_default_admin()
        print("Database initialized.")


def _is_authenticated() -> bool:
    user_id = session.get("user_id")
    if not user_id:
        return False

    participant = ParticipantService().get_by_id(user_id)
    if participant is None or not participant.is_active:
        session.clear()
        return False

    return True


app = create_app()
