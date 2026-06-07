from datetime import UTC, datetime

import pytest

from app.core.exceptions import ValidationError
from app.db.registry import DatabaseRegistry
from app.services.task import TaskService


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
