"""Lightweight Telegram notification helper (no aiogram dependency)."""

import httpx
import sentry_sdk

from app.core.logging import logger
from app.settings import get_settings

_API = "https://api.telegram.org/bot{token}/sendMessage"


async def notify_admin(text: str) -> None:
    """Send a message to the admin's Telegram chat. Fails silently."""
    settings = get_settings()
    if not settings.TELEGRAM_BOT_CHAT_TOKEN or not settings.TELEGRAM_ALLOWED_USER_ID:
        return

    url = _API.format(token=settings.TELEGRAM_BOT_CHAT_TOKEN)
    payload = {
        "chat_id": settings.TELEGRAM_ALLOWED_USER_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
    except Exception as exc:
        logger.warning(
            "Telegram notification failed",
            context={"error": str(exc)},
        )
        sentry_sdk.capture_exception(exc)
