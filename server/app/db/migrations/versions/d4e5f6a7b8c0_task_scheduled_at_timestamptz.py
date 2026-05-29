"""task scheduled_at timestamptz and timezone-aware mixin timestamps

Revision ID: d4e5f6a7b8c0
Revises: c3d4e5f6a7b8
Create Date: 2026-05-29 22:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "d4e5f6a7b8c0"
down_revision: str | None = "c3d4e5f6a7b8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_MIXIN_TABLES = (
    "users",
    "shortened_urls",
    "shared_files",
    "tasks",
    "reminders",
    "recipes",
    "feedback",
    "github_credentials",
    "tool_expenses",
    "tool_expense_categories",
)


def upgrade() -> None:
    op.alter_column(
        "tasks",
        "scheduled_at",
        existing_type=sa.String(length=50),
        type_=sa.DateTime(timezone=True),
        postgresql_using="(scheduled_at::timestamp AT TIME ZONE 'UTC')",
        existing_nullable=False,
    )

    for table in _MIXIN_TABLES:
        for column in ("created_at", "updated_at"):
            op.alter_column(
                table,
                column,
                existing_type=sa.DateTime(),
                type_=sa.DateTime(timezone=True),
                postgresql_using=f"({column} AT TIME ZONE 'UTC')",
                existing_nullable=False,
            )


def downgrade() -> None:
    for table in reversed(_MIXIN_TABLES):
        for column in ("updated_at", "created_at"):
            op.alter_column(
                table,
                column,
                existing_type=sa.DateTime(timezone=True),
                type_=sa.DateTime(),
                existing_nullable=False,
            )

    op.alter_column(
        "tasks",
        "scheduled_at",
        existing_type=sa.DateTime(timezone=True),
        type_=sa.String(length=50),
        postgresql_using="scheduled_at::text",
        existing_nullable=False,
    )
