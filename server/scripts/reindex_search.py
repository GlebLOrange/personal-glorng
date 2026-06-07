"""Backfill the search_documents index from all supported sources."""

import asyncio
import sys

from app.core.elasticsearch import init_elasticsearch, is_elasticsearch_enabled
from app.db.worker_registry import get_worker_registry
from app.services import elasticsearch_search
from app.services.search_indexers import SEARCH_REINDEXERS
from app.settings import get_settings


async def reindex_search() -> None:
    """Rebuild search documents from resume and MongoDB collections."""
    settings = get_settings()
    if settings.elasticsearch_enabled():
        await init_elasticsearch(settings.ELASTICSEARCH_URL)

    registry = await get_worker_registry()
    counts: dict[str, int] = {}
    for label, reindex_fn in SEARCH_REINDEXERS:
        counts[label] = await reindex_fn(registry)

    summary = " ".join(f"{label}={count}" for label, count in counts.items())
    print(f"Search reindex complete: {summary}")  # noqa: T201

    if is_elasticsearch_enabled() and registry.search is not None:
        rows = await registry.search.list(limit=10_000)
        es_count = await elasticsearch_search.bulk_index_documents(rows)
        print(f"Elasticsearch reindex complete: documents={es_count}")  # noqa: T201


def main() -> None:
    asyncio.run(reindex_search())


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print("reindex_search failed", file=sys.stderr)  # noqa: T201
        raise
