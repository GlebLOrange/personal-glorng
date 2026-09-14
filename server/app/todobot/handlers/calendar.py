"""Google Calendar OAuth connection handler."""

from urllib.parse import urlencode

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from app.core.google_oauth_state import (
    generate_google_oauth_state,
    store_google_oauth_state,
)
from app.db.registry import DatabaseRegistry
from app.settings import get_settings

router = Router()


def _oauth_keyboard(auth_url: str, *, reconnect: bool = False) -> InlineKeyboardMarkup:
    label = "Reconnect Google Calendar" if reconnect else "Connect Google Calendar"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=label, url=auth_url)],
        ],
    )


async def _build_auth_url(*, telegram_user_id: int) -> str | None:
    settings = get_settings()
    if not settings.GOOGLE_CLIENT_ID:
        return None

    state = generate_google_oauth_state()
    await store_google_oauth_state(
        state=state,
        telegram_user_id=telegram_user_id,
    )
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "https://www.googleapis.com/auth/calendar",
        "access_type": "offline",
        "prompt": "consent",
        "state": state,
    }
    return f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"


@router.message(Command("connect_calendar"))
async def cmd_connect_calendar(
    message: Message,
    registry: DatabaseRegistry,
) -> None:
    settings = get_settings()

    if not settings.GOOGLE_CLIENT_ID:
        await message.answer(
            "Google Calendar integration is not configured yet.",
        )
        return

    if not message.from_user:
        return

    cred = None
    if registry.credentials is not None:
        cred = await registry.credentials.get_google_for_telegram_user(
            message.from_user.id,
        )

    auth_url = await _build_auth_url(telegram_user_id=message.from_user.id)
    if not auth_url:
        await message.answer("Google Calendar integration is not configured yet.")
        return

    if cred:
        await message.answer(
            "📅 Google Calendar is *connected*.\n"
            "New tasks sync as events; Telegram and Calendar remind together.\n\n"
            "Need to re-link? Use the button below.",
            parse_mode="Markdown",
            reply_markup=_oauth_keyboard(auth_url, reconnect=True),
        )
        return

    await message.answer(
        "Click the button below to connect your Google Calendar:",
        reply_markup=_oauth_keyboard(auth_url),
    )
