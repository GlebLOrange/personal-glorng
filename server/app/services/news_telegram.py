"""Telegram publishing for curated news articles."""

import html
import re
from typing import Any

import httpx

from app.core.exceptions import ApiError
from app.core.json_lists import parse_json_string_list
from app.db.documents.news import NewsArticle
from app.settings import get_settings

_API = "https://api.telegram.org/bot{token}/sendMessage"
_HASHTAG_RE = re.compile(r"[^A-Za-z0-9_]+")


def _escape(value: str) -> str:
    """Escape dynamic text for Telegram HTML parse mode."""
    return html.escape(value, quote=True)


def _theme_tag(theme: str) -> str:
    """Return a safe Telegram hashtag."""
    cleaned = _HASHTAG_RE.sub("", theme.replace("-", "_"))
    return f"#{cleaned}" if cleaned else ""


def format_news_telegram_message(article: NewsArticle) -> str:
    """Format a curated news article for Telegram."""
    bullets = parse_json_string_list(article.bullets)[:3]
    themes = [_theme_tag(theme) for theme in parse_json_string_list(article.themes)]
    bullet_lines = "\n".join(f"• {_escape(bullet)}" for bullet in bullets)
    theme_line = " ".join(theme for theme in themes if theme)
    base = get_settings().BASE_URL.rstrip("/")
    parts = [
        f"<b>{_escape(article.title)}</b>",
        _escape(article.summary),
    ]
    if bullet_lines:
        parts.append(bullet_lines)
    if theme_line:
        parts.append(f"Themes: {theme_line}")
    parts.extend(
        [
            (
                f'Source: <a href="{_escape(article.source_url)}">'
                f"{_escape(article.source_name)}</a>"
            ),
            f"Read on site: {_escape(f'{base}/news/{article.slug}')}",
        ]
    )
    return "\n\n".join(parts)[:4096]


async def publish_news_article_to_telegram(article: NewsArticle) -> int:
    """Publish an article to the configured Telegram channel."""
    settings = get_settings()
    if not settings.NEWS_TELEGRAM_BOT_TOKEN or not settings.NEWS_TELEGRAM_CHANNEL_ID:
        raise ApiError(503, "News Telegram channel is not configured")
    payload = {
        "chat_id": settings.NEWS_TELEGRAM_CHANNEL_ID,
        "text": format_news_telegram_message(article),
        "parse_mode": "HTML",
        "disable_web_page_preview": False,
    }
    url = _API.format(token=settings.NEWS_TELEGRAM_BOT_TOKEN)
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
    data: dict[str, Any] = response.json()
    message_id = data.get("result", {}).get("message_id")
    if not isinstance(message_id, int):
        raise ApiError(502, "Telegram did not return a message id")
    return message_id
