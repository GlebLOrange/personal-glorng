"""add search_documents visibility check constraint

Revision ID: m7n8o9p0q1r2
Revises: l6m7n8o9p0q1
Create Date: 2026-06-07 18:00:00.000000
"""

from collections.abc import Sequence

from alembic import op

revision: str = "m7n8o9p0q1r2"
down_revision: str | None = "l6m7n8o9p0q1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_check_constraint(
        "ck_search_documents_visibility",
        "search_documents",
        "visibility IN ('public', 'admin')",
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_search_documents_visibility",
        "search_documents",
        type_="check",
    )
