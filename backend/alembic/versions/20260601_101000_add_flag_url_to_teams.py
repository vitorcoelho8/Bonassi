"""add flag url to teams

Revision ID: 20260601_101000
Revises: 20260601_100000
Create Date: 2026-06-01 10:10:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "20260601_101000"
down_revision = "20260601_100000"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("teams", sa.Column("flag_url", sa.String(length=255), nullable=True))


def downgrade() -> None:
    op.drop_column("teams", "flag_url")
