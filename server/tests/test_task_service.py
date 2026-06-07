from datetime import UTC, datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ValidationError
from app.services.task import TaskService


@pytest.mark.asyncio
async def test_create_task_sanitizes_via_task_text_fields(db: AsyncSession) -> None:
    svc = TaskService(db)
    task = await svc.create_task(
        telegram_user_id=123456789,
        title="  buy\x00 milk  ",
        scheduled_at=datetime(2026, 6, 1, 10, 0, tzinfo=UTC),
        description="  notes\x00  ",
        location="  home  ",
    )
    await db.commit()

    assert task.title == "buy milk"
    assert task.description == "notes"
    assert task.location == "home"


@pytest.mark.asyncio
async def test_create_task_rejects_blank_title(db: AsyncSession) -> None:
    svc = TaskService(db)
    with pytest.raises(ValidationError, match="Title must not be empty"):
        await svc.create_task(
            telegram_user_id=123456789,
            title="   \x00  ",
            scheduled_at=datetime(2026, 6, 1, 10, 0, tzinfo=UTC),
        )
