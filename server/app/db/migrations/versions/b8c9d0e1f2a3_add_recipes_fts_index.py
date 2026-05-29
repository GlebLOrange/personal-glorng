"""add recipes full-text search index

Revision ID: b8c9d0e1f2a3
Revises: a7b8c9d0e1f2
Create Date: 2026-05-29 20:00:00.000000
"""

from collections.abc import Sequence

from alembic import op

revision: str = "b8c9d0e1f2a3"
down_revision: str | None = "a7b8c9d0e1f2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

RECIPE_SEARCH_INDEX = "ix_recipes_search_vector"
RECIPE_SEARCH_EXPRESSION = """
    to_tsvector(
        'english',
        title || ' ' || ingredients || ' ' || steps || ' ' || coalesce(notes, '')
    )
"""


def upgrade() -> None:
    op.execute(
        f"CREATE INDEX {RECIPE_SEARCH_INDEX} ON recipes USING gin ({RECIPE_SEARCH_EXPRESSION})"
    )


def downgrade() -> None:
    op.drop_index(RECIPE_SEARCH_INDEX, table_name="recipes")
