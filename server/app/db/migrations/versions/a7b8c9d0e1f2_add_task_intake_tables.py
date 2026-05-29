"""add task intake tables

Revision ID: a7b8c9d0e1f2
Revises: f1a2b3c4d5e6
Create Date: 2026-05-29 18:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import ENUM, JSONB

revision: str = "a7b8c9d0e1f2"
down_revision: str | None = "f1a2b3c4d5e6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

intake_status = ENUM(
    "parsing",
    "clarifying",
    "ready",
    "confirmed",
    "cancelled",
    name="intake_status",
    create_type=False,
)

_CREATE_ENUM_SQL = """
DO $$ BEGIN
    CREATE TYPE intake_status AS ENUM (
        'parsing', 'clarifying', 'ready', 'confirmed', 'cancelled'
    );
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;
"""


def upgrade() -> None:
    op.execute(sa.text(_CREATE_ENUM_SQL))

    op.create_table(
        "telegram_inbound_messages",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("telegram_user_id", sa.BigInteger(), nullable=False),
        sa.Column("telegram_message_id", sa.BigInteger(), nullable=False),
        sa.Column("chat_id", sa.BigInteger(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("metadata_json", JSONB(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("telegram_message_id"),
    )
    op.create_index(
        op.f("ix_telegram_inbound_messages_telegram_user_id"),
        "telegram_inbound_messages",
        ["telegram_user_id"],
    )

    op.create_table(
        "task_intakes",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column(
            "inbound_message_id",
            sa.Integer(),
            sa.ForeignKey("telegram_inbound_messages.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "status",
            intake_status,
            nullable=False,
            server_default="parsing",
        ),
        sa.Column("draft_json", JSONB(), nullable=True),
        sa.Column("confidence_json", JSONB(), nullable=True),
        sa.Column(
            "clarification_turns_json",
            JSONB(),
            nullable=True,
            server_default="[]",
        ),
        sa.Column(
            "clarification_rounds",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "task_id",
            sa.Integer(),
            sa.ForeignKey("tasks.id", ondelete="SET NULL"),
            nullable=True,
        ),
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
    )
    op.create_index(
        op.f("ix_task_intakes_inbound_message_id"),
        "task_intakes",
        ["inbound_message_id"],
    )
    op.create_index(
        op.f("ix_task_intakes_task_id"),
        "task_intakes",
        ["task_id"],
    )

    op.add_column("tasks", sa.Column("intake_id", sa.Integer(), nullable=True))
    op.add_column(
        "tasks",
        sa.Column("jira_issue_key", sa.String(length=50), nullable=True),
    )
    op.create_foreign_key(
        "fk_tasks_intake_id",
        "tasks",
        "task_intakes",
        ["intake_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(op.f("ix_tasks_intake_id"), "tasks", ["intake_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_tasks_intake_id"), table_name="tasks")
    op.drop_constraint("fk_tasks_intake_id", "tasks", type_="foreignkey")
    op.drop_column("tasks", "jira_issue_key")
    op.drop_column("tasks", "intake_id")

    op.drop_index(op.f("ix_task_intakes_task_id"), table_name="task_intakes")
    op.drop_index(
        op.f("ix_task_intakes_inbound_message_id"),
        table_name="task_intakes",
    )
    op.drop_table("task_intakes")

    op.drop_index(
        op.f("ix_telegram_inbound_messages_telegram_user_id"),
        table_name="telegram_inbound_messages",
    )
    op.drop_table("telegram_inbound_messages")

    op.execute(sa.text("DROP TYPE IF EXISTS intake_status"))
