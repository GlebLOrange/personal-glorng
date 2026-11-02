from datetime import UTC, datetime, timedelta

import pytest

from app.core.exceptions import ConflictError, ValidationError
from app.db.documents.task import TaskStatus
from app.db.registry import DatabaseRegistry
from app.services.task import TaskService
from tests.factories import create_task


@pytest.mark.asyncio
async def test_create_task_sanitizes_via_task_text_fields(
    registry: DatabaseRegistry,
) -> None:
    svc = TaskService(registry)
    task = await svc.create_task(
        telegram_user_id=123456789,
        title="  buy\x00 milk  ",
        scheduled_at=datetime(2026, 6, 1, 10, 0, tzinfo=UTC),
        description="  notes\x00  ",
        location="  home  ",
    )

    assert task.title == "buy milk"
    assert task.description == "notes"
    assert task.location == "home"


@pytest.mark.asyncio
async def test_create_task_rejects_blank_title(registry: DatabaseRegistry) -> None:
    svc = TaskService(registry)
    with pytest.raises(ValidationError, match="Title must not be empty"):
        await svc.create_task(
            telegram_user_id=123456789,
            title="   \x00  ",
            scheduled_at=datetime(2026, 6, 1, 10, 0, tzinfo=UTC),
        )


@pytest.mark.asyncio
async def test_change_status_rejects_complete_for_future_task(
    registry: DatabaseRegistry,
) -> None:
    """Future tasks cannot be marked completed."""
    svc = TaskService(registry)
    task = await create_task(
        registry,
        telegram_user_id=123456789,
        title="Later",
        scheduled_at=datetime.now(UTC) + timedelta(days=2),
    )
    with pytest.raises(ConflictError, match="future"):
        await svc.change_status(task_id=task.id, new_status=TaskStatus.COMPLETED)


@pytest.mark.asyncio
async def test_get_closest_pending_tasks_merges_by_distance(
    registry: DatabaseRegistry,
) -> None:
    """Closest pending prefers nearer overdue and upcoming."""
    svc = TaskService(registry)
    now = datetime.now(UTC)
    near_future = await create_task(
        registry,
        telegram_user_id=42,
        title="Soon",
        scheduled_at=now + timedelta(hours=1),
    )
    await create_task(
        registry,
        telegram_user_id=42,
        title="Far",
        scheduled_at=now + timedelta(days=10),
    )
    near_past = await create_task(
        registry,
        telegram_user_id=42,
        title="Overdue",
        scheduled_at=now - timedelta(hours=2),
    )
    closest = await svc.get_closest_pending_tasks(telegram_user_id=42, limit=2)
    ids = {task.id for task in closest}
    assert near_future.id in ids
    assert near_past.id in ids
    assert len(closest) == 2
