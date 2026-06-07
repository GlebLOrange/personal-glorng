"""user profile and preferences

Revision ID: g1h2i3j4k5l6
Revises: f2a3b4c5d6e7
Create Date: 2026-06-07
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "g1h2i3j4k5l6"
down_revision: str | None = "f2a3b4c5d6e7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "users", sa.Column("display_name", sa.String(length=100), nullable=True)
    )
    op.add_column(
        "users",
        sa.Column(
            "timezone", sa.String(length=64), server_default="UTC", nullable=False
        ),
    )
    op.add_column(
        "users",
        sa.Column("preferences", sa.JSON(), server_default="{}", nullable=False),
    )


def downgrade() -> None:
    op.drop_column("users", "preferences")
    op.drop_column("users", "timezone")
    op.drop_column("users", "display_name")
