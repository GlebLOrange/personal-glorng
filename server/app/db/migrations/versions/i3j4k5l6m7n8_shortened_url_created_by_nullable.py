"""shortened_url created_by nullable

Revision ID: i3j4k5l6m7n8
Revises: h2i3j4k5l6m7
Create Date: 2026-06-07
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "i3j4k5l6m7n8"
down_revision: str | None = "h2i3j4k5l6m7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column(
        "shortened_urls",
        "created_by",
        existing_type=sa.Integer(),
        nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "shortened_urls",
        "created_by",
        existing_type=sa.Integer(),
        nullable=False,
    )
