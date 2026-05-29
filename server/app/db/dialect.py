"""Database dialect helpers."""

from functools import lru_cache


@lru_cache
def get_database_dialect() -> str:
    """Return SQLAlchemy dialect name derived from DATABASE_URL."""
    from app.settings import get_settings

    url = get_settings().DATABASE_URL
    if url.startswith("postgresql"):
        return "postgresql"
    if url.startswith("sqlite"):
        return "sqlite"
    return url.split("://", 1)[0].split("+", 1)[0]
