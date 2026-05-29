"""Shared recipe full-text search constants."""

RECIPE_SEARCH_CONFIG = "english"
RECIPE_SEARCH_INDEX = "ix_recipes_search_vector"
RECIPE_FTS_EXPRESSION = (
    "to_tsvector('english', title || ' ' || ingredients || ' ' || steps || ' ' || "
    "coalesce(notes, ''))"
)
