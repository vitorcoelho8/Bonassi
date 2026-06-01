"""create teams table

Revision ID: 20260601_100000
Revises: 20260601_090000
Create Date: 2026-06-01 10:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "20260601_100000"
down_revision = "20260601_090000"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "teams",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("normalized_name", sa.String(length=120), nullable=False),
        sa.Column("fifa_code", sa.String(length=10), nullable=True),
        sa.Column("group_name", sa.String(length=10), nullable=True),
        sa.Column("is_brazil", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_confirmed", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("fifa_code", name="uq_teams_fifa_code"),
        sa.UniqueConstraint("name", name="uq_teams_name"),
        sa.UniqueConstraint("normalized_name", name="uq_teams_normalized_name"),
    )


def downgrade() -> None:
    op.drop_table("teams")
