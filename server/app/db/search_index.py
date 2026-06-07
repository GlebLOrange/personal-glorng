"""Shared search_documents full-text search constants."""

SEARCH_INDEX_CONFIG = "english"
SEARCH_INDEX_NAME = "ix_search_documents_search_vector"
SEARCH_FTS_EXPRESSION = (
    "to_tsvector('english', title || ' ' || body)"
)
