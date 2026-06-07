"""Tests for reminder scheduling helpers."""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.reminder import Reminder
from app.services.task import create_reminder
from app.workers.job_names import JobName
from app.workers.scheduling import schedule_reminder, supersede_unsent_reminders
from tests.factories import create_task


@pytest.mark.asyncio
@patch("app.workers.scheduling.get_job_queue")
async def test_schedule_reminder_enqueues_and_stores_job_id(
    mock_get_queue: AsyncMock,
    db: AsyncSession,
) -> None:
    mock_queue = AsyncMock()
    mock_queue.enqueue = AsyncMock(return_value="job-abc123")
    mock_get_queue.return_value = mock_queue
    task = await create_task(db)
    remind_at = datetime.now(UTC) + timedelta(hours=1)
    reminder = await create_reminder(db, task_id=task.id, remind_at=remind_at)

    result = await schedule_reminder(db, reminder)

    mock_queue.enqueue.assert_awaited_once_with(
        JobName.SEND_REMINDER,
        reminder.id,
        eta=remind_at,
    )
    assert result.job_id == "job-abc123"


@pytest.mark.asyncio
@patch("app.workers.scheduling.get_job_queue")
async def test_schedule_reminder_skips_past_due(
    mock_get_queue: AsyncMock,
    db: AsyncSession,
) -> None:
    mock_queue = AsyncMock()
    mock_get_queue.return_value = mock_queue
    task = await create_task(db)
    remind_at = datetime.now(UTC) - timedelta(minutes=5)
    reminder = await create_reminder(db, task_id=task.id, remind_at=remind_at)

    await schedule_reminder(db, reminder)

    mock_queue.enqueue.assert_not_awaited()


@pytest.mark.asyncio
@patch("app.workers.scheduling.get_job_queue")
async def test_supersede_unsent_reminders_aborts_and_deletes(
    mock_get_queue: AsyncMock,
    db: AsyncSession,
) -> None:
    mock_queue = AsyncMock()
    mock_queue.enqueue = AsyncMock(return_value="job-new")
    mock_queue.revoke = AsyncMock()
    mock_get_queue.return_value = mock_queue
    task = await create_task(db)
    old_at = datetime.now(UTC) + timedelta(hours=2)
    new_at = datetime.now(UTC) + timedelta(hours=3)

    old = await create_reminder(db, task_id=task.id, remind_at=old_at, job_id="job-old")
    keep = await create_reminder(db, task_id=task.id, remind_at=new_at)

    await supersede_unsent_reminders(db, task.id, exclude_id=keep.id)
    await db.commit()

    mock_queue.revoke.assert_awaited_once_with("job-old")
    count = await db.scalar(select(func.count()).select_from(Reminder))
    assert count == 1
    remaining = await db.get(Reminder, keep.id)
    assert remaining is not None
    assert await db.get(Reminder, old.id) is None
