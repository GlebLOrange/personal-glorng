"""add todobot tables

Revision ID: c4e8f2a91b3d
Revises: a10996a0b1f2
Create Date: 2026-05-25 15:50:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import ENUM

revision: str = "c4e8f2a91b3d"
down_revision: str | None = "a10996a0b1f2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

task_status = ENUM(
    "pending",
    "completed",
    "not_completed",
    "postponed",
    "cancelled",
    name="task_status",
    create_type=False,
)
sync_action = ENUM("create", "update", "delete", name="sync_action", create_type=False)
sync_status = ENUM(
    "pending", "completed", "failed", name="sync_status", create_type=False
)

_CREATE_ENUM_SQL = """
DO $$ BEGIN
    CREATE TYPE {name} AS ENUM ({values});
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;
"""


def _create_enum_safe(name: str, values: list[str]) -> None:
    formatted = ", ".join(f"'{v}'" for v in values)
    op.execute(sa.text(_CREATE_ENUM_SQL.format(name=name, values=formatted)))


def upgrade() -> None:
    _create_enum_safe(
        "task_status",
        ["pending", "completed", "not_completed", "postponed", "cancelled"],
    )
    _create_enum_safe("sync_action", ["create", "update", "delete"])
    _create_enum_safe("sync_status", ["pending", "completed", "failed"])

    op.create_table(
        "tasks",
        sa.Column("telegram_user_id", sa.BigInteger(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("location", sa.String(length=255), nullable=True),
        sa.Column("scheduled_at", sa.String(length=50), nullable=False),
        sa.Column(
            "status",
            task_status,
            nullable=False,
            server_default="pending",
        ),
        sa.Column("google_event_id", sa.String(length=255), nullable=True),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_tasks_telegram_user_id"),
        "tasks",
        ["telegram_user_id"],
    )

    op.create_table(
        "reminders",
        sa.Column(
            "task_id",
            sa.Integer(),
            sa.ForeignKey("tasks.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "remind_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "sent",
            sa.Boolean(),
            nullable=False,
            server_default="false",
        ),
        sa.Column("arq_job_id", sa.String(length=100), nullable=True),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_reminders_task_id"),
        "reminders",
        ["task_id"],
    )

    op.create_table(
        "task_status_history",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column(
            "task_id",
            sa.Integer(),
            sa.ForeignKey("tasks.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("old_status", sa.String(length=20), nullable=False),
        sa.Column("new_status", sa.String(length=20), nullable=False),
        sa.Column(
            "changed_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_task_status_history_task_id"),
        "task_status_history",
        ["task_id"],
    )

    op.create_table(
        "google_sync_queue",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column(
            "task_id",
            sa.Integer(),
            sa.ForeignKey("tasks.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("action", sync_action, nullable=False),
        sa.Column(
            "attempts",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column(
            "next_retry_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "status",
            sync_status,
            nullable=False,
            server_default="pending",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "error_notified",
            sa.Boolean(),
            nullable=False,
            server_default="false",
        ),
        sa.Column(
            "google_event_id",
            sa.String(length=255),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_google_sync_queue_task_id"),
        "google_sync_queue",
        ["task_id"],
    )

    op.create_table(
        "google_credentials",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("telegram_user_id", sa.BigInteger(), nullable=False),
        sa.Column("refresh_token", sa.String(length=512), nullable=False),
        sa.Column(
            "calendar_id",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column("sync_token", sa.String(length=255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("telegram_user_id"),
    )
    op.create_index(
        op.f("ix_google_credentials_telegram_user_id"),
        "google_credentials",
        ["telegram_user_id"],
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_google_credentials_telegram_user_id"),
        table_name="google_credentials",
    )
    op.drop_table("google_credentials")

    op.drop_index(
        op.f("ix_google_sync_queue_task_id"),
        table_name="google_sync_queue",
    )
    op.drop_table("google_sync_queue")

    op.drop_index(
        op.f("ix_task_status_history_task_id"),
        table_name="task_status_history",
    )
    op.drop_table("task_status_history")

    op.drop_index(op.f("ix_reminders_task_id"), table_name="reminders")
    op.drop_table("reminders")

    op.drop_index(
        op.f("ix_tasks_telegram_user_id"),
        table_name="tasks",
    )
    op.drop_table("tasks")

    op.execute(sa.text("DROP TYPE IF EXISTS sync_status"))
    op.execute(sa.text("DROP TYPE IF EXISTS sync_action"))
    op.execute(sa.text("DROP TYPE IF EXISTS task_status"))
