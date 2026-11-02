"""Compatibility shim; implementation lives in ``app.services.news.telegram``."""

from app.services.news.telegram import (
    format_news_telegram_message,
    publish_news_article_to_telegram,
)

__all__ = ["format_news_telegram_message", "publish_news_article_to_telegram"]
