"""add search_documents table with FTS index

Revision ID: l6m7n8o9p0q1
Revises: k5l6m7n8o9p0
Create Date: 2026-06-07 12:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

from app.db.search_index import SEARCH_FTS_EXPRESSION, SEARCH_INDEX_NAME

revision: str = "l6m7n8o9p0q1"
down_revision: str | None = "k5l6m7n8o9p0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "search_documents",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("source_type", sa.String(length=32), nullable=False),
        sa.Column("source_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=512), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("url", sa.String(length=512), server_default="/", nullable=False),
        sa.Column(
            "visibility", sa.String(length=16), server_default="public", nullable=False
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
        sa.UniqueConstraint(
            "source_type", "source_id", name="uq_search_documents_source"
        ),
    )
    op.create_index(
        "ix_search_documents_source_type",
        "search_documents",
        ["source_type"],
        unique=False,
    )
    op.create_index(
        "ix_search_documents_source_id",
        "search_documents",
        ["source_id"],
        unique=False,
    )
    op.create_index(
        "ix_search_documents_visibility",
        "search_documents",
        ["visibility"],
        unique=False,
    )
    op.create_index(
        SEARCH_INDEX_NAME,
        "search_documents",
        [sa.text(SEARCH_FTS_EXPRESSION)],
        postgresql_using="gin",
    )


def downgrade() -> None:
    op.drop_index(SEARCH_INDEX_NAME, table_name="search_documents")
    op.drop_index("ix_search_documents_visibility", table_name="search_documents")
    op.drop_index("ix_search_documents_source_id", table_name="search_documents")
    op.drop_index("ix_search_documents_source_type", table_name="search_documents")
    op.drop_table("search_documents")
