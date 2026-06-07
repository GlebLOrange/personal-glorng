"""align fts index definitions with declarative models

Revision ID: n8o9p0q1r2s3
Revises: m7n8o9p0q1r2
Create Date: 2026-06-07
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

from app.db.recipe_search import RECIPE_FTS_EXPRESSION, RECIPE_SEARCH_INDEX
from app.db.search_index import SEARCH_FTS_EXPRESSION, SEARCH_INDEX_NAME

revision: str = "n8o9p0q1r2s3"
down_revision: str | None = "m7n8o9p0q1r2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_index(RECIPE_SEARCH_INDEX, table_name="recipes")
    op.create_index(
        RECIPE_SEARCH_INDEX,
        "recipes",
        [sa.text(RECIPE_FTS_EXPRESSION)],
        postgresql_using="gin",
    )
    op.drop_index(SEARCH_INDEX_NAME, table_name="search_documents")
    op.create_index(
        SEARCH_INDEX_NAME,
        "search_documents",
        [sa.text(SEARCH_FTS_EXPRESSION)],
        postgresql_using="gin",
    )


def downgrade() -> None:
    op.drop_index(SEARCH_INDEX_NAME, table_name="search_documents")
    op.create_index(
        SEARCH_INDEX_NAME,
        "search_documents",
        [sa.text(SEARCH_FTS_EXPRESSION)],
        postgresql_using="gin",
    )
    op.drop_index(RECIPE_SEARCH_INDEX, table_name="recipes")
    op.execute(
        f"CREATE INDEX {RECIPE_SEARCH_INDEX} ON recipes USING gin ("
        "to_tsvector("
        "'english', "
        "title || ' ' || ingredients || ' ' || steps || ' ' || coalesce(notes, '')"
        "))"
    )
