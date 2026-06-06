"""add expense source and category monthly budget

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c1
Create Date: 2026-06-06 12:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "e5f6a7b8c9d0"
down_revision: str | None = "d4e5f6a7b8c1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "tool_expenses",
        sa.Column(
            "source",
            sa.String(length=16),
            server_default="web_admin",
            nullable=False,
        ),
    )
    op.add_column(
        "tool_expense_categories",
        sa.Column("monthly_budget", sa.Numeric(precision=12, scale=2), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("tool_expense_categories", "monthly_budget")
    op.drop_column("tool_expenses", "source")
