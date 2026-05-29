"""add tool_expense_categories table

Revision ID: c3d4e5f6a7b8
Revises: d0e1f2a3b4c5
Create Date: 2026-05-29 12:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "c3d4e5f6a7b8"
down_revision: str | None = "d0e1f2a3b4c5"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_DEFAULT_CATEGORIES = ("Groceries", "Home", "Transport")


def upgrade() -> None:
    op.create_table(
        "tool_expense_categories",
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.Column("sort_order", sa.Integer(), server_default="0", nullable=False),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    table = sa.table(
        "tool_expense_categories",
        sa.column("name", sa.String),
        sa.column("sort_order", sa.Integer),
    )
    op.bulk_insert(
        table,
        [{"name": name, "sort_order": index} for index, name in enumerate(_DEFAULT_CATEGORIES)],
    )

    conn = op.get_bind()
    rows = conn.execute(
        sa.text(
            "SELECT DISTINCT category FROM tool_expenses "
            "WHERE category IS NOT NULL AND category != ''",
        ),
    )
    existing = {row[0] for row in rows}
    missing = sorted(existing - set(_DEFAULT_CATEGORIES))
    if missing:
        op.bulk_insert(
            table,
            [
                {"name": name, "sort_order": len(_DEFAULT_CATEGORIES) + index}
                for index, name in enumerate(missing)
            ],
        )


def downgrade() -> None:
    op.drop_table("tool_expense_categories")
