"""Sample news seeding for core dev seed."""

from app.core.logging import logger
from app.db.registry import DatabaseRegistry
from app.db.seed.builders.demo import build_demo_news_articles, build_demo_news_sources

SAMPLE_NEWS_COUNT = 8


async def seed_news(registry: DatabaseRegistry) -> None:
    """Insert sample news sources and articles when collections are empty."""
    if registry.news is None or registry.news_sources is None:
        msg = "News repositories are not initialized"
        raise RuntimeError(msg)

    source_count = await registry.news_sources.count()
    article_count = await registry.news.count()
    if source_count or article_count:
        logger.info(
            "News already seeded",
            context={"sources": source_count, "articles": article_count},
        )
        return

    sources = []
    for source in build_demo_news_sources(SAMPLE_NEWS_COUNT):
        sources.append(await registry.news_sources.insert(source))

    articles = build_demo_news_articles(sources, SAMPLE_NEWS_COUNT)
    for article in articles:
        await registry.news.insert(article)

    logger.info(
        "Seeded sample news",
        context={"sources": len(sources), "articles": len(articles)},
    )
