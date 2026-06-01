"""add prediction points and bonus workflow

Revision ID: 20260531_161000
Revises: 20260531_155000
Create Date: 2026-05-31 16:10:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "20260531_161000"
down_revision = "20260531_155000"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "predictions",
        sa.Column("points", sa.Integer(), nullable=False, server_default="0"),
    )
    op.alter_column("predictions", "points", server_default=None)

    op.add_column("bonus_answers", sa.Column("bonus_type", sa.String(length=80), nullable=True))
    op.add_column("bonus_answers", sa.Column("evidence_text", sa.String(length=255), nullable=True))
    op.add_column("bonus_answers", sa.Column("referral_name", sa.String(length=120), nullable=True))
    op.add_column("bonus_answers", sa.Column("referral_phone", sa.String(length=30), nullable=True))
    op.add_column(
        "bonus_answers",
        sa.Column("status", sa.String(length=30), nullable=False, server_default="PENDING"),
    )

    op.execute("UPDATE bonus_answers SET bonus_type = UPPER(question_key) WHERE bonus_type IS NULL")
    op.execute("UPDATE bonus_answers SET evidence_text = answer WHERE evidence_text IS NULL")
    op.alter_column("bonus_answers", "bonus_type", existing_type=sa.String(length=80), nullable=False)
    op.alter_column("bonus_answers", "status", server_default=None)


def downgrade() -> None:
    op.drop_column("bonus_answers", "status")
    op.drop_column("bonus_answers", "referral_phone")
    op.drop_column("bonus_answers", "referral_name")
    op.drop_column("bonus_answers", "evidence_text")
    op.drop_column("bonus_answers", "bonus_type")
    op.drop_column("predictions", "points")
