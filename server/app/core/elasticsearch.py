from elasticsearch import AsyncElasticsearch

from app.core.logging import logger

_client: AsyncElasticsearch | None = None
_enabled = False


async def init_elasticsearch(url: str) -> None:
    """Connect to Elasticsearch when a URL is configured."""
    global _client, _enabled
    if not url.strip():
        return

    _client = AsyncElasticsearch(url)
    _enabled = True
    logger.info("Elasticsearch connected", context={"url": url})


async def close_elasticsearch() -> None:
    global _client, _enabled
    if _client is not None:
        await _client.close()
        _client = None
    _enabled = False


def is_elasticsearch_enabled() -> bool:
    return _enabled and _client is not None


def get_elasticsearch_client() -> AsyncElasticsearch:
    if _client is None:
        msg = "Elasticsearch not initialized. Call init_elasticsearch() first."
        raise RuntimeError(msg)
    return _client
