"""Google Calendar OAuth connection, status hub, and month busy-grid."""

from datetime import UTC, datetime
from urllib.parse import urlencode
from zoneinfo import ZoneInfo

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from app.core.google_oauth_state import (
    generate_google_oauth_state,
    store_google_oauth_state,
)
from app.core.utils import as_utc, format_scheduled_at, local_now
from app.db.documents.task import TaskStatus
from app.db.registry import DatabaseRegistry
from app.services.task import sync_calendar_for_telegram_user
from app.settings import get_settings
from app.todobot.keyboards.menu import main_menu
from app.todobot.keyboards.task import calendar_hub, month_day_buttons
from app.todobot.utils.oneshot import format_month_grid

router = Router()


def _oauth_keyboard(auth_url: str, *, reconnect: bool = False) -> InlineKeyboardMarkup:
    label = (
        "reconnect google calendar" if reconnect else "connect google calendar"
    )
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


async def _is_connected(registry: DatabaseRegistry, telegram_user_id: int) -> bool:
    if registry.credentials is None:
        return False
    cred = await registry.credentials.get_google_for_telegram_user(telegram_user_id)
    return cred is not None


async def send_calendar_hub(message: Message, registry: DatabaseRegistry) -> None:
    """Connected calendar hub: Sync now · Reconnect · Open month."""
    _ = registry
    if not message.from_user:
        return
    auth_url = await _build_auth_url(telegram_user_id=message.from_user.id)
    await message.answer(
        "📅 *Google Calendar*\n"
        "Status: *connected*\n\n"
        "Sync pending tasks, open this month, or reconnect.",
        parse_mode="Markdown",
        reply_markup=calendar_hub(reconnect_url=auth_url),
    )


async def send_month_view(
    message: Message,
    registry: DatabaseRegistry,
    *,
    year: int | None = None,
    month: int | None = None,
) -> None:
    """Reply with month grid + interactive busy-day buttons (bot pending only)."""
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
    busy_days = sorted(
        {
            as_utc(task.scheduled_at).astimezone(tz).day
            for task in tasks
            if task.scheduled_at
        },
    )
    await message.answer(
        f"```\n{text}\n```",
        parse_mode="Markdown",
        reply_markup=month_day_buttons(year=year, month=month, busy_days=busy_days),
    )


async def open_calendar_entry(message: Message, registry: DatabaseRegistry) -> None:
    """Menu Calendar / welcome inline: hub when linked, else OAuth connect."""
    if not message.from_user:
        return
    connected = await _is_connected(registry, message.from_user.id)
    if connected:
        await sync_calendar_for_telegram_user(
            registry,
            telegram_user_id=message.from_user.id,
        )
        await send_calendar_hub(message, registry)
        return
    await cmd_connect_calendar(message, registry)


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
        await send_calendar_hub(message, registry)
        return

    await message.answer(
        "Click the button below to connect your Google Calendar:",
        reply_markup=_oauth_keyboard(auth_url),
    )


@router.callback_query(F.data.startswith("cal:"))
async def handle_calendar_callbacks(
    callback: CallbackQuery,
    registry: DatabaseRegistry,
) -> None:
    if not callback.data or not callback.message or not callback.from_user:
        return
    parts = callback.data.split(":")
    action = parts[1] if len(parts) > 1 else ""
    await callback.answer()

    if action == "hub":
        await send_calendar_hub(callback.message, registry)
        return
    if action == "month":
        await send_month_view(callback.message, registry)
        return
    if action == "sync":
        n = await sync_calendar_for_telegram_user(
            registry,
            telegram_user_id=callback.from_user.id,
        )
        await callback.message.answer(
            f"Sync finished ({n} queue action(s)).",
            reply_markup=main_menu(),
        )
        return
    if action == "day" and len(parts) == 3:
        day_iso = parts[2]
        if registry.tasks is None:
            return
        settings = get_settings()
        tz = ZoneInfo(settings.TIMEZONE)
        day = datetime.fromisoformat(day_iso).replace(tzinfo=tz)
        start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start.replace(hour=23, minute=59, second=59)
        tasks = await registry.tasks.list_for_user_between(
            callback.from_user.id,
            start=start.astimezone(UTC),
            end=end.astimezone(UTC),
            status=TaskStatus.PENDING,
        )
        if not tasks:
            await callback.message.answer("No pending tasks that day.")
            return
        lines = [f"*{day_iso}*", ""]
        for task in tasks:
            when = format_scheduled_at(task.scheduled_at) if task.scheduled_at else "—"
            lines.append(f"• {task.title} — {when}")
        await callback.message.answer(
            "\n".join(lines),
            parse_mode="Markdown",
            reply_markup=main_menu(),
        )
