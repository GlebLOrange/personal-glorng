"""rename expense tables to drop tool_ prefix

Revision ID: o9p0q1r2s3t4
Revises: n8o9p0q1r2s3
Create Date: 2026-06-10
"""

from collections.abc import Sequence

from alembic import op

revision: str = "o9p0q1r2s3t4"
down_revision: str | None = "n8o9p0q1r2s3"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.rename_table("tool_expense_categories", "expense_categories")
    op.rename_table("tool_expenses", "expenses")


def downgrade() -> None:
    op.rename_table("expenses", "tool_expenses")
    op.rename_table("expense_categories", "tool_expense_categories")
