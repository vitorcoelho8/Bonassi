"""add brazil path fields to matches

Revision ID: 20260601_090000
Revises: 20260531_161000
Create Date: 2026-06-01 09:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "20260601_090000"
down_revision = "20260531_161000"
branch_labels = None
depends_on = None


def upgrade() -> None:
    existing_columns = _existing_columns()

    if "phase" not in existing_columns:
        op.add_column("matches", sa.Column("phase", sa.String(length=40), nullable=True))

    if "round_order" not in existing_columns:
        op.add_column("matches", sa.Column("round_order", sa.Integer(), nullable=True))

    if "is_brazil_match" not in existing_columns:
        op.add_column(
            "matches",
            sa.Column("is_brazil_match", sa.Boolean(), nullable=False, server_default=sa.true()),
        )

    if "is_knockout" not in existing_columns:
        op.add_column(
            "matches",
            sa.Column("is_knockout", sa.Boolean(), nullable=False, server_default=sa.false()),
        )

    if "created_manually_by_admin" not in existing_columns:
        op.add_column(
            "matches",
            sa.Column(
                "created_manually_by_admin",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            ),
        )

    op.execute(
        """
        UPDATE matches
        SET
            phase = COALESCE(phase, 'GROUP_STAGE'),
            round_order = COALESCE(round_order, 1),
            is_brazil_match = COALESCE(is_brazil_match, TRUE),
            is_knockout = COALESCE(is_knockout, FALSE),
            created_manually_by_admin = COALESCE(created_manually_by_admin, FALSE)
        """
    )


def downgrade() -> None:
    existing_columns = _existing_columns()

    for column_name in (
        "created_manually_by_admin",
        "is_knockout",
        "is_brazil_match",
        "round_order",
        "phase",
    ):
        if column_name in existing_columns:
            op.drop_column("matches", column_name)


def _existing_columns() -> set[str]:
    inspector = sa.inspect(op.get_bind())
    return {column["name"] for column in inspector.get_columns("matches")}
