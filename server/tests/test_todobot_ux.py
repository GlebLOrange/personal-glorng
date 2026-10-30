"""Tests for todobot welcome dashboard and dual at-start reminders."""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Chat, Message, User

from app.core.utils import as_utc
from app.db.registry import DatabaseRegistry
from app.services.calendar import _build_event_body, _reminder_minutes_for_task
from app.services.task import TaskService, create_with_sync
from app.todobot.handlers.start import (
    build_help_text,
    build_welcome_text,
    menu_restart,
)
from app.todobot.keyboards.menu import (
    LABEL_GUIDED_TASK,
    LABEL_QUICK_TASK,
    main_menu,
    welcome_inline,
)
from app.todobot.keyboards.task import confirmation, my_task_detail
from app.todobot.utils.calendar_status import (
    LINE_ADDED,
    LINE_NOT_LINKED,
    LINE_PENDING,
    calendar_post_create_line,
)
from tests.factories import create_google_credential, create_task


def test_main_menu_has_quick_and_guided_without_expenses() -> None:
    """Reply keyboard exposes Quick/Guided and hides expenses."""
    markup = main_menu()
    labels = {btn.text for row in markup.keyboard for btn in row}
    assert LABEL_QUICK_TASK in labels
    assert LABEL_GUIDED_TASK in labels
    assert "log expense" not in labels
    assert "expense" not in " ".join(labels).lower()


def test_welcome_inline_fixed_menu_layout() -> None:
    """Welcome inline: quick|guided, tasks|calendar, help|restart."""
    disconnected = welcome_inline(calendar_connected=False)
    rows = [[btn.text for btn in row] for row in disconnected.inline_keyboard]
    data = [btn.callback_data for row in disconnected.inline_keyboard for btn in row]
    assert rows[0] == ["⚡ quick task", "🧭 guided task"]
    assert rows[1] == ["📋 tasks", "📅 connect calendar"]
    assert rows[2] == ["❓ help", "🔄 restart"]
    assert "w:tasks" in data
    assert not any(d and d.startswith("w:t:") for d in data)

    connected = welcome_inline(calendar_connected=True)
    assert connected.inline_keyboard[1][1].text == "📅 calendar"

    reply_rows = [[btn.text for btn in row] for row in main_menu().keyboard]
    assert reply_rows[0] == [LABEL_QUICK_TASK, LABEL_GUIDED_TASK]
    assert reply_rows[1] == ["📋 tasks", "📅 calendar"]
    assert reply_rows[2] == ["❓ help", "🔄 restart"]


def test_action_buttons_are_lowercase_with_icons() -> None:
    """Confirm and detail action labels are lowercase with emoji icons."""
    conf = [btn.text for row in confirmation().inline_keyboard for btn in row]
    assert conf == ["✅ confirm", "✏️ edit", "❌ cancel"]

    detail = [btn.text for row in my_task_detail(9).inline_keyboard for btn in row]
    assert "✅ mark done" in detail
    assert "🗑 remove" in detail
    assert "✏️ edit" in detail
    assert "◀️ back" in detail
    assert "🏠 main" in detail


def test_build_welcome_text_no_task_list() -> None:
    """Welcome shows status/counters; no per-task bullets or tap-to-edit hint."""
    connected = build_welcome_text(
        calendar_connected=True,
        has_open_tasks=True,
        timezone_name="Europe/Berlin",
        overdue_count=0,
        today_count=0,
        total_open=1,
    )
    assert "Calendar: *connected*" in connected
    assert "Europe/Berlin" in connected
    assert "*Open:* 1" in connected
    assert "*Open tasks:*" not in connected
    assert "tap a task" not in connected.lower()
    assert "📋 *tasks*" in connected
    assert "Use the buttons below to navigate." in connected

    empty = build_welcome_text(
        calendar_connected=False,
        has_open_tasks=False,
        timezone_name="Europe/Berlin",
        overdue_count=0,
        today_count=0,
        total_open=0,
    )
    assert "not connected" in empty
    assert "No open tasks" in empty
    assert "Tips" in empty


def test_build_help_text_is_richer_than_welcome() -> None:
    """Help covers capture, manage, calendar, reminders."""
    help_text = build_help_text(timezone_name="Europe/Berlin")
    assert "TodoBot help" in help_text
    assert "idle message" in help_text
    assert "Reminders" in help_text
    assert "Calendar" in help_text
    assert "Europe/Berlin" in help_text


@pytest.mark.asyncio
async def test_menu_restart_clears_state_and_sends_welcome(
    registry: DatabaseRegistry,
) -> None:
    """Restart deletes tracked msgs, clears FSM, and shows /start welcome."""
    storage = MemoryStorage()
    key = StorageKey(bot_id=1, chat_id=123456, user_id=123456)
    state = FSMContext(storage=storage, key=key)
    await state.update_data(_msg_ids=[101, 102], title="half-done")

    message = MagicMock(spec=Message)
    message.from_user = User(id=123456, is_bot=False, first_name="Test")
    message.chat = Chat(id=123456, type="private")
    message.answer = AsyncMock()
    message.bot = MagicMock()
    message.bot.delete_message = AsyncMock()

    with patch(
        "app.todobot.handlers.start._send_welcome",
        new_callable=AsyncMock,
    ) as mock_welcome:
        await menu_restart(message, state, registry)

    assert message.bot.delete_message.await_count == 2
    assert await state.get_data() == {}
    mock_welcome.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_with_sync_schedules_static_reminders(
    registry: DatabaseRegistry,
) -> None:
    """Create always schedules at-start plus 90/60/30 early reminders."""
    scheduled = datetime.now(UTC) + timedelta(days=2)
    with (
        patch(
            "app.workers.scheduling.schedule_reminder",
            new_callable=AsyncMock,
        ) as mock_sched,
        patch("app.workers.tasks.process_sync_queue", new_callable=AsyncMock),
    ):
        task = await create_with_sync(
            registry,
            telegram_user_id=123456,
            title="Static reminders",
            scheduled_at=scheduled,
            reminder_minutes=15,
        )

    assert registry.tasks is not None
    reminders = await registry.tasks.list_reminders_for_task(task.id)
    deltas = sorted(
        int((scheduled - as_utc(rem.remind_at)).total_seconds() // 60)
        for rem in reminders
    )
    assert deltas == [0, 30, 60, 90]
    assert mock_sched.await_count == 4


@pytest.mark.asyncio
async def test_reminder_minutes_includes_zero_for_google(
    registry: DatabaseRegistry,
) -> None:
    """Static reminders map to Google popup minutes including 0."""
    scheduled = datetime.now(UTC) + timedelta(days=1)
    with (
        patch(
            "app.workers.scheduling.schedule_reminder",
            new_callable=AsyncMock,
        ),
        patch("app.workers.tasks.process_sync_queue", new_callable=AsyncMock),
    ):
        task = await TaskService(registry).create_with_sync(
            telegram_user_id=99,
            title="Zero popup",
            scheduled_at=scheduled,
        )

    minutes = await _reminder_minutes_for_task(registry, task)
    assert sorted(minutes) == [0, 30, 60, 90]

    body = _build_event_body(task, reminder_minutes=minutes)
    overrides = body["reminders"]["overrides"]
    assert {"method": "popup", "minutes": 0} in overrides
    assert {"method": "popup", "minutes": 90} in overrides


@pytest.mark.asyncio
async def test_calendar_post_create_line_not_linked(
    registry: DatabaseRegistry,
) -> None:
    """Unlinked Telegram user gets connect-calendar copy."""
    task = await create_task(registry, telegram_user_id=4242)
    line = await calendar_post_create_line(
        registry,
        telegram_user_id=4242,
        task=task,
    )
    assert line == LINE_NOT_LINKED


@pytest.mark.asyncio
async def test_calendar_post_create_line_added_after_reload(
    registry: DatabaseRegistry,
) -> None:
    """Stale task without event id still reports Added after DB reload."""
    telegram_user_id = 5151
    await create_google_credential(registry, telegram_user_id=telegram_user_id)
    stale = await create_task(
        registry,
        telegram_user_id=telegram_user_id,
        google_event_id=None,
    )
    assert registry.tasks is not None
    await registry.tasks.update_fields(stale.id, google_event_id="evt-synced")
    line = await calendar_post_create_line(
        registry,
        telegram_user_id=telegram_user_id,
        task=stale,
    )
    assert line == LINE_ADDED
    assert stale.google_event_id is None


@pytest.mark.asyncio
async def test_calendar_post_create_line_pending_when_linked_without_event(
    registry: DatabaseRegistry,
) -> None:
    """Linked but unsynced task gets Sync-now pending copy."""
    telegram_user_id = 6161
    await create_google_credential(registry, telegram_user_id=telegram_user_id)
    task = await create_task(
        registry,
        telegram_user_id=telegram_user_id,
        google_event_id=None,
    )
    line = await calendar_post_create_line(
        registry,
        telegram_user_id=telegram_user_id,
        task=task,
    )
    assert line == LINE_PENDING
