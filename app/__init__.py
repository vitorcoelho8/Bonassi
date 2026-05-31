from flask import Flask, redirect, render_template, url_for
from flask.cli import with_appcontext

from app.core.config import Config
from app.database.extensions import db
from app.modules.auth.auth import is_authenticated
from app.modules.auth.routes.auth_routes import auth_bp
from app.modules.competition.routes.competition_routes import competition_bp


def create_app(config_class: type[Config] = Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    register_commands(app)

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(competition_bp, url_prefix="/api/competitions")

    @app.get("/")
    def index():
        if is_authenticated():
            return redirect(url_for("home_page"))

        return redirect(url_for("login_page"))

    @app.get("/api/health")
    def health_check() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/login")
    def login_page() -> str:
        if is_authenticated():
            return redirect(url_for("home_page"))

        return render_template("login.html")

    @app.get("/home")
    def home_page():
        if not is_authenticated():
            return redirect(url_for("login_page"))

        return render_template("home.html")

    return app


def register_commands(app: Flask) -> None:
    @app.cli.command("init-db")
    @with_appcontext
    def init_db_command() -> None:
        from app.database.bootstrap import ensure_default_admin

        ensure_default_admin()
        print("Database initialized.")
