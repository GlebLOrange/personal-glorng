"""Search indexing helpers for curated news."""

from app.core.json_lists import parse_json_string_list
from app.db.documents.news import NewsArticle
from app.db.documents.search import SearchVisibility
from app.db.registry import DatabaseRegistry
from app.services.search_index import (
    SearchDocumentInput,
    remove_by_source,
    upsert_document,
)
from app.services.search_source_types import SearchSourceType

NEWS_SOURCE_TYPE = SearchSourceType.NEWS


def _news_document(article: NewsArticle) -> SearchDocumentInput:
    """Build a search document for a news article."""
    bullets = " ".join(parse_json_string_list(article.bullets))
    themes = ", ".join(parse_json_string_list(article.themes))
    body = "\n".join(
        part
        for part in (
            article.summary,
            bullets,
            f"Source: {article.source_name}",
            f"Themes: {themes}" if themes else "",
        )
        if part
    )
    return SearchDocumentInput(
        source_type=NEWS_SOURCE_TYPE,
        source_id=article.id,
        title=article.title,
        body=body,
        url=f"/news/{article.slug}",
        visibility=SearchVisibility.PUBLIC,
    )


async def index_news_article(
    registry: DatabaseRegistry,
    article: NewsArticle,
) -> None:
    """Upsert a published article into search, or remove unpublished articles."""
    if article.status != "published":
        await remove_news_article(registry, article.id)
        return
    await upsert_document(registry, _news_document(article))


async def remove_news_article(registry: DatabaseRegistry, article_id: int) -> None:
    """Remove a news article from search."""
    await remove_by_source(registry, NEWS_SOURCE_TYPE, article_id)
