"""Google Calendar OAuth connection and month busy-grid."""

from datetime import UTC, datetime
from urllib.parse import urlencode
from zoneinfo import ZoneInfo

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from app.core.google_oauth_state import (
    generate_google_oauth_state,
    store_google_oauth_state,
)
from app.core.utils import local_now
from app.db.documents.task import TaskStatus
from app.db.registry import DatabaseRegistry
from app.settings import get_settings
from app.todobot.keyboards.menu import main_menu
from app.todobot.utils.oneshot import format_month_grid

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


async def send_month_view(
    message: Message,
    registry: DatabaseRegistry,
    *,
    year: int | None = None,
    month: int | None = None,
) -> None:
    """Reply with a plain-text month grid of pending busy days."""
    if not message.from_user:
        return
    if registry.tasks is None:
        await message.answer(
            "Tasks are unavailable right now.",
            reply_markup=main_menu(),
        )
        return

    settings = get_settings()
    now = local_now()
    year = year if year is not None else now.year
    month = month if month is not None else now.month

    tz = ZoneInfo(settings.TIMEZONE)
    start_local = datetime(year, month, 1, tzinfo=tz)
    if month == 12:
        end_local = datetime(year + 1, 1, 1, tzinfo=tz)
    else:
        end_local = datetime(year, month + 1, 1, tzinfo=tz)

    tasks = await registry.tasks.list_for_user_between(
        message.from_user.id,
        start=start_local.astimezone(UTC),
        end=end_local.astimezone(UTC),
        status=TaskStatus.PENDING,
    )
    text = format_month_grid(
        year=year,
        month=month,
        tasks=tasks,
        timezone_name=settings.TIMEZONE,
    )
    await message.answer(
        f"```\n{text}\n```",
        parse_mode="Markdown",
        reply_markup=main_menu(),
    )


@router.message(Command("month"))
async def cmd_month(
    message: Message,
    registry: DatabaseRegistry,
) -> None:
    await send_month_view(message, registry)


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
            "Need to re-link? Use the button below.\n"
            "Busy days this month: /month",
            parse_mode="Markdown",
            reply_markup=_oauth_keyboard(auth_url, reconnect=True),
        )
        return

    await message.answer(
        "Click the button below to connect your Google Calendar:",
        reply_markup=_oauth_keyboard(auth_url),
    )
