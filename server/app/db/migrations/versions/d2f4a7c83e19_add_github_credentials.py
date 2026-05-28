"""add github_credentials

Revision ID: d2f4a7c83e19
Revises: 6a8afe17ea7b
Create Date: 2026-05-27 03:15:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "d2f4a7c83e19"
down_revision: str | None = "6a8afe17ea7b"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "github_credentials",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("github_user_id", sa.BigInteger(), nullable=False),
        sa.Column("github_username", sa.String(length=255), nullable=False),
        sa.Column("access_token", sa.String(length=512), nullable=False),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_github_credentials_user_id"),
        "github_credentials",
        ["user_id"],
        unique=True,
    )
    op.create_index(
        op.f("ix_github_credentials_github_user_id"),
        "github_credentials",
        ["github_user_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_github_credentials_github_user_id"),
        table_name="github_credentials",
    )
    op.drop_index(
        op.f("ix_github_credentials_user_id"),
        table_name="github_credentials",
    )
    op.drop_table("github_credentials")
