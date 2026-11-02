"""Lightweight Telegram helpers (httpx; no aiogram dependency)."""

from dataclasses import dataclass

import httpx
import sentry_sdk

from app.core.exceptions import ServiceUnavailableError, ValidationError
from app.core.logging import logger
from app.settings import get_settings

_API_BASE = "https://api.telegram.org/bot{token}/{method}"
_SEND_MESSAGE = "https://api.telegram.org/bot{token}/sendMessage"


@dataclass(frozen=True, slots=True)
class TodobotPingResult:
    """Outcome of a todobot token + outbound DM healthcheck."""

    ok: bool
    bot_username: str | None
    bot_id: int | None
    message_sent: bool
    detail: str


async def notify_admin(text: str) -> None:
    """Send a message to the admin's Telegram chat. Fails silently."""
    settings = get_settings()
    if not settings.TELEGRAM_BOT_CHAT_TOKEN or not settings.TELEGRAM_ALLOWED_USER_ID:
        return

    url = _SEND_MESSAGE.format(token=settings.TELEGRAM_BOT_CHAT_TOKEN)
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


async def ping_todobot() -> TodobotPingResult:
    """Verify todobot token via getMe and DM the allowlisted user.

    Does not prove the todobot polling process is running.
    """
    settings = get_settings()
    token = settings.TELEGRAM_BOT_TO_DO_TOKEN
    chat_id = settings.TELEGRAM_ALLOWED_USER_ID
    if not token:
        raise ValidationError("TELEGRAM_BOT_TO_DO_TOKEN is not configured")
    if not chat_id:
        raise ValidationError("TELEGRAM_ALLOWED_USER_ID is not configured")

    get_me_url = _API_BASE.format(token=token, method="getMe")
    send_url = _SEND_MESSAGE.format(token=token)

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            me_resp = await client.get(get_me_url)
            me_resp.raise_for_status()
            me_body = me_resp.json()
            if not me_body.get("ok"):
                raise ServiceUnavailableError(
                    me_body.get("description") or "Telegram getMe failed",
                )
            result = me_body.get("result") or {}
            bot_id = result.get("id")
            bot_username = result.get("username")
            username_label = f"@{bot_username}" if bot_username else "TodoBot"
            text = f"TodoBot ping OK · {username_label}"

            send_resp = await client.post(
                send_url,
                json={
                    "chat_id": chat_id,
                    "text": text,
                    "disable_web_page_preview": True,
                },
            )
            send_resp.raise_for_status()
            send_body = send_resp.json()
            if not send_body.get("ok"):
                raise ServiceUnavailableError(
                    send_body.get("description") or "Telegram sendMessage failed",
                )
    except ValidationError:
        raise
    except ServiceUnavailableError:
        raise
    except Exception as exc:
        logger.warning(
            "Todobot ping failed",
            context={"error": str(exc)},
        )
        sentry_sdk.capture_exception(exc)
        raise ServiceUnavailableError("Telegram todobot ping failed") from exc

    return TodobotPingResult(
        ok=True,
        bot_username=bot_username if isinstance(bot_username, str) else None,
        bot_id=bot_id if isinstance(bot_id, int) else None,
        message_sent=True,
        detail=text,
    )
