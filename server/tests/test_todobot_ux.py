"""Tests for todobot welcome dashboard and dual at-start reminders."""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Chat, Message, User

from app.core.utils import as_utc
from app.db.documents.task import Task, TaskStatus
from app.db.registry import DatabaseRegistry
from app.services.calendar import _build_event_body, _reminder_minutes_for_task
from app.services.task import TaskService, create_with_sync
from app.todobot.handlers.start import build_welcome_text, menu_restart
from app.todobot.keyboards.menu import (
    LABEL_GUIDED_TASK,
    LABEL_LOG_EXPENSE,
    LABEL_QUICK_TASK,
    main_menu,
)


def test_main_menu_has_quick_and_guided_without_expenses() -> None:
    """Reply keyboard exposes Quick/Guided and hides expenses."""
    markup = main_menu()
    labels = {btn.text for row in markup.keyboard for btn in row}
    assert LABEL_QUICK_TASK in labels
    assert LABEL_GUIDED_TASK in labels
    assert LABEL_LOG_EXPENSE not in labels


def test_build_welcome_text_lists_pending_and_calendar() -> None:
    """Welcome dashboard shows calendar status and open tasks."""
    task = Task(
        telegram_user_id=1,
        title="Buy milk",
        scheduled_at=datetime(2026, 12, 1, 10, 0, tzinfo=UTC),
        status=TaskStatus.PENDING,
    )
    connected = build_welcome_text(calendar_connected=True, pending_tasks=[task])
    assert "Calendar: *connected*" in connected
    assert "Buy milk" in connected

    empty = build_welcome_text(calendar_connected=False, pending_tasks=[])
    assert "not connected" in empty
    assert "No open tasks" in empty


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
    mock_welcome.assert_awaited_once_with(message, registry)


@pytest.mark.asyncio
async def test_create_with_sync_always_schedules_at_start(
    registry: DatabaseRegistry,
) -> None:
    """No early remind still creates an at-event Telegram reminder."""
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
            title="At start only",
            scheduled_at=scheduled,
            reminder_minutes=None,
        )

    assert registry.tasks is not None
    reminders = await registry.tasks.list_reminders_for_task(task.id)
    assert len(reminders) == 1
    assert abs((as_utc(reminders[0].remind_at) - scheduled).total_seconds()) < 1
    assert mock_sched.await_count == 1


@pytest.mark.asyncio
async def test_create_with_sync_early_plus_at_start(
    registry: DatabaseRegistry,
) -> None:
    """Early heads-up plus at-start yields two reminder rows."""
    scheduled = datetime.now(UTC) + timedelta(days=3)
    with (
        patch(
            "app.workers.scheduling.schedule_reminder",
            new_callable=AsyncMock,
        ),
        patch("app.workers.tasks.process_sync_queue", new_callable=AsyncMock),
    ):
        task = await create_with_sync(
            registry,
            telegram_user_id=123456,
            title="Early and start",
            scheduled_at=scheduled,
            reminder_minutes=15,
        )

    assert registry.tasks is not None
    reminders = await registry.tasks.list_reminders_for_task(task.id)
    deltas = sorted(
        int((scheduled - as_utc(rem.remind_at)).total_seconds() // 60)
        for rem in reminders
    )
    assert deltas == [0, 15]


@pytest.mark.asyncio
async def test_reminder_minutes_includes_zero_for_google(
    registry: DatabaseRegistry,
) -> None:
    """At-start reminder maps to Google popup minutes=0."""
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
            reminder_minutes=30,
        )

    minutes = await _reminder_minutes_for_task(registry, task)
    assert 0 in minutes
    assert 30 in minutes

    body = _build_event_body(task, reminder_minutes=minutes)
    overrides = body["reminders"]["overrides"]
    assert {"method": "popup", "minutes": 0} in overrides
    assert {"method": "popup", "minutes": 30} in overrides
