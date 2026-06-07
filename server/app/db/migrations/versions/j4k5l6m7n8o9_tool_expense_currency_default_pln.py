"""tool expense currency default PLN

Revision ID: j4k5l6m7n8o9
Revises: i3j4k5l6m7n8
Create Date: 2026-06-07

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "j4k5l6m7n8o9"
down_revision: str | None = "i3j4k5l6m7n8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column(
        "tool_expenses",
        "currency",
        server_default="PLN",
        existing_type=sa.String(length=3),
    )


def downgrade() -> None:
    op.alter_column(
        "tool_expenses",
        "currency",
        server_default="USD",
        existing_type=sa.String(length=3),
    )
