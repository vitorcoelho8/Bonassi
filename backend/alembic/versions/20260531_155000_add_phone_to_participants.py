"""add phone to participants

Revision ID: 20260531_155000
Revises: 20260531_153900
Create Date: 2026-05-31 15:50:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "20260531_155000"
down_revision = "20260531_153900"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("participants", "email", existing_type=sa.String(length=255), nullable=True)
    op.alter_column("participants", "password_hash", existing_type=sa.String(length=255), nullable=True)


def downgrade() -> None:
    op.alter_column("participants", "password_hash", existing_type=sa.String(length=255), nullable=False)
    op.alter_column("participants", "email", existing_type=sa.String(length=255), nullable=False)
