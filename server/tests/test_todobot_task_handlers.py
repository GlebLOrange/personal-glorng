"""Handler-level tests for Telegram task create and status update."""

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import CallbackQuery, Chat, Message, User

from app.db.documents.task import SyncStatus, TaskStatus
from app.db.registry import DatabaseRegistry
from app.todobot.handlers.reminder import handle_postpone_datetime, handle_reminder_action
from app.todobot.handlers.task_create import confirm_task
from app.todobot.handlers.task_manage import cmd_tasks, handle_status_update
from app.todobot.keyboards.task import completion_options
from tests.factories import create_task


def _fsm_context(*, user_id: int = 123456, chat_id: int = 123456) -> FSMContext:
    storage = MemoryStorage()
    key = StorageKey(bot_id=1, chat_id=chat_id, user_id=user_id)
    return FSMContext(storage=storage, key=key)


def _user(*, user_id: int = 123456) -> User:
    return User(id=user_id, is_bot=False, first_name="Test")


def _chat(*, chat_id: int = 123456) -> Chat:
    return Chat(id=chat_id, type="private")


def _callback(
    *,
    data: str | None,
    user_id: int = 123456,
    chat_id: int = 123456,
) -> CallbackQuery:
    message = MagicMock(spec=Message)
    message.chat = _chat(chat_id=chat_id)
    message.answer = AsyncMock()
    callback = MagicMock(spec=CallbackQuery)
    callback.data = data
    callback.message = message
    callback.from_user = _user(user_id=user_id)
    callback.answer = AsyncMock()
    callback.bot = None
    return callback


def _message(*, user_id: int = 123456, chat_id: int = 123456, text: str = "") -> Message:
    message = MagicMock(spec=Message)
    message.from_user = _user(user_id=user_id)
    message.chat = _chat(chat_id=chat_id)
    message.text = text
    message.answer = AsyncMock()
    message.bot = None
    return message


@pytest.mark.asyncio
@patch("app.workers.tasks.process_sync_queue", new_callable=AsyncMock)
@patch("app.workers.queue.get_job_queue")
async def test_confirm_guided_creates_task_and_sync_queue(
    mock_get_queue: MagicMock,
    mock_process: AsyncMock,
    registry: DatabaseRegistry,
) -> None:
    """Guided confirm (no intake_id) persists a task and calendar sync row."""
    mock_get_queue.return_value = AsyncMock()
    state = _fsm_context()
    await state.update_data(
        title="Buy milk",
        date="2026-12-01",
        time="10:00",
        reminder_minutes=None,
    )
    callback = _callback(data="confirm:yes")

    await confirm_task(callback, state, registry)

    assert registry.tasks is not None
    tasks = await registry.tasks.list_for_user(123456, limit=10)
    assert len(tasks) == 1
    assert tasks[0].title == "Buy milk"

    sync_doc = await registry.mongo_db.google_sync_queue.find_one(
        {"task_id": tasks[0].id},
    )
    assert sync_doc is not None
    assert sync_doc["status"] == SyncStatus.PENDING.value
    callback.message.answer.assert_awaited()
    assert await state.get_data() == {}


@pytest.mark.asyncio
async def test_handle_status_update_marks_completed(
    registry: DatabaseRegistry,
) -> None:
    """status:{id}:completed callback updates the task status."""
    task = await create_task(registry, telegram_user_id=123456, title="Status me")
    callback = _callback(data=f"status:{task.id}:completed")

    await handle_status_update(callback, registry)

    assert registry.tasks is not None
    updated = await registry.tasks.get(task.id)
    assert updated.status == TaskStatus.COMPLETED
    callback.message.answer.assert_awaited()


@pytest.mark.asyncio
async def test_handle_status_update_invalid_payload_is_noop(
    registry: DatabaseRegistry,
) -> None:
    """Malformed or unknown status callbacks must not crash or mutate."""
    task = await create_task(registry, telegram_user_id=123456, title="Leave me")

    await handle_status_update(_callback(data="status:bad"), registry)
    await handle_status_update(_callback(data=f"status:{task.id}:bogus"), registry)
    await handle_status_update(_callback(data=None), registry)

    assert registry.tasks is not None
    unchanged = await registry.tasks.get(task.id)
    assert unchanged.status == TaskStatus.PENDING


@pytest.mark.asyncio
async def test_reminder_complete_marks_task_completed(
    registry: DatabaseRegistry,
) -> None:
    """raction complete marks the task completed."""
    task = await create_task(registry, telegram_user_id=123456, title="Done soon")
    state = _fsm_context()
    callback = _callback(data=f"raction:{task.id}:complete")

    await handle_reminder_action(callback, state, registry)

    assert registry.tasks is not None
    updated = await registry.tasks.get(task.id)
    assert updated.status == TaskStatus.COMPLETED


@pytest.mark.asyncio
async def test_reminder_postpone_reschedules_task(
    registry: DatabaseRegistry,
) -> None:
    """Postpone action + datetime reply moves scheduled_at."""
    task = await create_task(registry, telegram_user_id=123456, title="Move me")
    original = task.scheduled_at
    state = _fsm_context()
    callback = _callback(data=f"raction:{task.id}:postpone")

    await handle_reminder_action(callback, state, registry)

    message = _message(text="2026-12-15 15:00")
    await handle_postpone_datetime(message, state, registry)

    assert registry.tasks is not None
    updated = await registry.tasks.get(task.id)
    assert updated.scheduled_at != original
    assert updated.scheduled_at.year == 2026
    assert updated.scheduled_at.month == 12
    assert updated.scheduled_at.day == 15
    message.answer.assert_awaited()


@pytest.mark.asyncio
async def test_cmd_tasks_sends_completion_options(
    registry: DatabaseRegistry,
) -> None:
    """/tasks lists each pending task with status buttons."""
    task = await create_task(registry, telegram_user_id=123456, title="Button me")
    message = _message()

    await cmd_tasks(message, registry)

    assert message.answer.await_count >= 2
    task_call = message.answer.await_args_list[-1]
    assert "Button me" in task_call.args[0]
    markup: Any = task_call.kwargs.get("reply_markup")
    assert markup is not None
    expected = completion_options(task.id)
    assert markup.inline_keyboard == expected.inline_keyboard
