"""Backfill the search_documents index from all supported sources."""

import asyncio
import sys

from app.db.session import get_session_factory
from app.services.search_indexers import SEARCH_REINDEXERS


async def reindex_search() -> None:
    """Rebuild search documents from resume and database tables."""
    factory = get_session_factory()
    async with factory() as db:
        counts: dict[str, int] = {}
        for label, reindex_fn in SEARCH_REINDEXERS:
            counts[label] = await reindex_fn(db)

        await db.commit()
        summary = " ".join(f"{label}={count}" for label, count in counts.items())
        print(f"Search reindex complete: {summary}")  # noqa: T201


def main() -> None:
    asyncio.run(reindex_search())


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print("reindex_search failed", file=sys.stderr)  # noqa: T201
        raise
