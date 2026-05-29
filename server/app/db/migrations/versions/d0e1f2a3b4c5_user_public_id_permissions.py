"""user public_id and permissions

Revision ID: d0e1f2a3b4c5
Revises: c9d0e1f2a3b4
Create Date: 2026-05-29
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "d0e1f2a3b4c5"
down_revision: str | None = "c9d0e1f2a3b4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("users", sa.Column("public_id", sa.Uuid(), nullable=True))
    op.add_column(
        "users",
        sa.Column("permissions", sa.JSON(), server_default="[]", nullable=False),
    )
    op.execute(
        sa.text(
            "UPDATE users SET public_id = gen_random_uuid() WHERE public_id IS NULL"
        )
    )
    op.execute(
        sa.text(
            "UPDATE users SET permissions = '[\"platform:superuser\"]'::json "
            "WHERE is_admin = true",
        ),
    )
    op.alter_column("users", "public_id", nullable=False)
    op.create_index(op.f("ix_users_public_id"), "users", ["public_id"], unique=True)
    op.drop_column("users", "is_admin")


def downgrade() -> None:
    op.add_column(
        "users",
        sa.Column("is_admin", sa.Boolean(), server_default=sa.false(), nullable=False),
    )
    op.execute(
        sa.text(
            "UPDATE users SET is_admin = true "
            "WHERE permissions::text LIKE '%platform:superuser%'",
        ),
    )
    op.drop_index(op.f("ix_users_public_id"), table_name="users")
    op.drop_column("users", "permissions")
    op.drop_column("users", "public_id")
