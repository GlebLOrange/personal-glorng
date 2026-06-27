"""Demo news seeding."""

from app.db.registry import DatabaseRegistry
from app.db.seed.builders.demo import build_demo_news_articles, build_demo_news_sources


async def seed_demo_news(registry: DatabaseRegistry, count: int = 20) -> int:
    """Insert deterministic news sources and articles."""
    if registry.news is None or registry.news_sources is None:
        msg = "News repositories are not initialized"
        raise RuntimeError(msg)

    source_count = min(count, 20)
    sources = []
    for source in build_demo_news_sources(source_count):
        sources.append(await registry.news_sources.insert(source))

    articles = build_demo_news_articles(sources, source_count)
    for article in articles:
        await registry.news.insert(article)
    return len(articles)
