from sqlalchemy import Index, Integer, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, BaseModelMixin
from app.db.recipe_search import RECIPE_FTS_EXPRESSION, RECIPE_SEARCH_INDEX


class Recipe(BaseModelMixin, Base):
    __tablename__ = "recipes"
    __table_args__ = (
        Index(
            RECIPE_SEARCH_INDEX,
            text(RECIPE_FTS_EXPRESSION),
            postgresql_using="gin",
        ),
    )

    title: Mapped[str] = mapped_column(String(255))
    ingredients: Mapped[str] = mapped_column(Text)
    steps: Mapped[str] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    tags: Mapped[str] = mapped_column(Text, server_default="[]")
    image_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    prep_time: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cook_time: Mapped[int | None] = mapped_column(Integer, nullable=True)
    servings: Mapped[int | None] = mapped_column(Integer, nullable=True)
