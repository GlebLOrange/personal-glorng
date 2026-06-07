"""Rename reminders.arq_job_id to job_id and clear stale broker ids."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "k5l6m7n8o9p0"
down_revision: str | None = "j4k5l6m7n8o9"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column(
        "reminders",
        "arq_job_id",
        new_column_name="job_id",
        existing_type=sa.String(length=100),
        existing_nullable=True,
    )
    op.execute(
        "UPDATE reminders SET job_id = NULL WHERE sent = false AND job_id IS NOT NULL",
    )


def downgrade() -> None:
    op.alter_column(
        "reminders",
        "job_id",
        new_column_name="arq_job_id",
        existing_type=sa.String(length=100),
        existing_nullable=True,
    )
