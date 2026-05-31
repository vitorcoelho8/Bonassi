from werkzeug.security import generate_password_hash

from app.database.extensions import db
from app.modules.auth.models.user_model import User


DEFAULT_ADMIN_EMAIL = "admin@bonassi.com"
DEFAULT_ADMIN_NAME = "Administrador"
DEFAULT_ADMIN_PASSWORD = "123456a!"


def ensure_default_admin() -> None:
    User.__table__.create(bind=db.engine, checkfirst=True)

    admin = User.query.filter_by(email=DEFAULT_ADMIN_EMAIL).first()
    password_hash = generate_password_hash(DEFAULT_ADMIN_PASSWORD)

    if admin is None:
        admin = User(
            name=DEFAULT_ADMIN_NAME,
            email=DEFAULT_ADMIN_EMAIL,
            password_hash=password_hash,
            is_active=True,
        )
        db.session.add(admin)
    else:
        admin.name = DEFAULT_ADMIN_NAME
        admin.password_hash = password_hash
        admin.is_active = True

    db.session.commit()
