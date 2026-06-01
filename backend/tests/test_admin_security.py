from __future__ import annotations

import unittest

from werkzeug.security import check_password_hash

from app.admin.service import ensure_default_admin
from app.config import Config
from app.database import db
from app.main import create_app
from app.participants.models import Participant
from app.participants.service import ParticipantService

# Import relationship targets before db.create_all().
from app.bonus import models as _bonus_models  # noqa: F401
from app.predictions import models as _prediction_models  # noqa: F401


class BaseAdminSecurityConfig(Config):
    TESTING = True
    SECRET_KEY = "test-secret"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
    ADMIN_EMAIL = "admin-security@test.local"
    ADMIN_NAME = "Admin Test"


class DevelopmentAdminConfig(BaseAdminSecurityConfig):
    IS_PRODUCTION = False
    SESSION_COOKIE_SECURE = False
    ADMIN_PASSWORD = None


class ProductionWithoutAdminPasswordConfig(BaseAdminSecurityConfig):
    IS_PRODUCTION = True
    SESSION_COOKIE_SECURE = True
    ADMIN_PASSWORD = None


class ProductionWeakAdminPasswordConfig(BaseAdminSecurityConfig):
    IS_PRODUCTION = True
    SESSION_COOKIE_SECURE = True
    ADMIN_PASSWORD = "123456a!"


class ProductionStrongAdminPasswordConfig(BaseAdminSecurityConfig):
    IS_PRODUCTION = True
    SESSION_COOKIE_SECURE = True
    ADMIN_PASSWORD = "A-strong-admin-password-2026!"


class AdminSecurityTestCase(unittest.TestCase):
    def tearDown(self) -> None:
        if hasattr(self, "context"):
            db.session.remove()
            db.drop_all()
            self.context.pop()

    def _push_app(self, config_class: type[Config]) -> None:
        self.app = create_app(config_class)
        self.context = self.app.app_context()
        self.context.push()
        db.create_all()

    def test_production_requires_admin_password(self) -> None:
        self._push_app(ProductionWithoutAdminPasswordConfig)

        with self.assertRaisesRegex(RuntimeError, "ADMIN_PASSWORD must be configured in production."):
            ensure_default_admin()

    def test_production_rejects_known_weak_admin_password(self) -> None:
        self._push_app(ProductionWeakAdminPasswordConfig)

        with self.assertRaisesRegex(RuntimeError, "ADMIN_PASSWORD is too weak for production."):
            ensure_default_admin()

    def test_production_creates_admin_with_hashed_configured_password(self) -> None:
        self._push_app(ProductionStrongAdminPasswordConfig)

        ensure_default_admin()

        admin = Participant.query.filter_by(email=ProductionStrongAdminPasswordConfig.ADMIN_EMAIL).one()
        self.assertEqual(admin.role, "admin")
        self.assertNotEqual(admin.password_hash, ProductionStrongAdminPasswordConfig.ADMIN_PASSWORD)
        self.assertTrue(check_password_hash(admin.password_hash, ProductionStrongAdminPasswordConfig.ADMIN_PASSWORD))

    def test_admin_login_still_works_with_configured_password(self) -> None:
        self._push_app(ProductionStrongAdminPasswordConfig)
        ensure_default_admin()

        admin = ParticipantService().authenticate(
            ProductionStrongAdminPasswordConfig.ADMIN_EMAIL,
            ProductionStrongAdminPasswordConfig.ADMIN_PASSWORD,
        )

        self.assertEqual(admin.email, ProductionStrongAdminPasswordConfig.ADMIN_EMAIL)
        self.assertEqual(admin.role, "admin")

    def test_development_allows_local_fallback_password(self) -> None:
        self._push_app(DevelopmentAdminConfig)

        ensure_default_admin()

        admin = Participant.query.filter_by(email=DevelopmentAdminConfig.ADMIN_EMAIL).one()
        self.assertTrue(check_password_hash(admin.password_hash, "123456a!"))


if __name__ == "__main__":
    unittest.main()
