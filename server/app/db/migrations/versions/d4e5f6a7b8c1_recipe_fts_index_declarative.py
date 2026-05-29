"""recreate recipes FTS index via Alembic create_index

Revision ID: d4e5f6a7b8c1
Revises: d4e5f6a7b8c0
Create Date: 2026-05-29 22:05:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

from app.db.recipe_search import RECIPE_FTS_EXPRESSION, RECIPE_SEARCH_INDEX

revision: str = "d4e5f6a7b8c1"
down_revision: str | None = "d4e5f6a7b8c0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(sa.text(f"DROP INDEX IF EXISTS {RECIPE_SEARCH_INDEX}"))
    op.create_index(
        RECIPE_SEARCH_INDEX,
        "recipes",
        [sa.text(RECIPE_FTS_EXPRESSION)],
        postgresql_using="gin",
    )


def downgrade() -> None:
    op.drop_index(RECIPE_SEARCH_INDEX, table_name="recipes")
    op.execute(
        sa.text(
            f"CREATE INDEX {RECIPE_SEARCH_INDEX} ON recipes USING gin "
            f"({RECIPE_FTS_EXPRESSION})",
        ),
    )
