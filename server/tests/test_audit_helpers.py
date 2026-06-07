from datetime import UTC, datetime

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.audit_event import AuditActorType, AuditCategory, AuditSource, AuditEvent
from app.services.audit import domain_event
from app.services.task import TaskService


def test_domain_event_builds_domain_record() -> None:
    record = domain_event(
        action="task.created",
        resource_type="task",
        resource_id=42,
        actor_id=7,
        metadata={"title": "Buy milk"},
    )
    assert record.category == AuditCategory.DOMAIN
    assert record.action == "task.created"
    assert record.resource_type == "task"
    assert record.resource_id == 42
    assert record.actor_id == 7
    assert record.source == AuditSource.WEB_ADMIN


@pytest.mark.asyncio
async def test_create_task_records_domain_audit(db: AsyncSession) -> None:
    svc = TaskService(db)
    task = await svc.create_task(
        telegram_user_id=123456789,
        title="Audit test",
        scheduled_at=datetime(2026, 6, 1, 10, 0, tzinfo=UTC),
    )
    await db.commit()

    result = await db.execute(
        select(AuditEvent).where(
            AuditEvent.resource_type == "task",
            AuditEvent.resource_id == task.id,
            AuditEvent.action == "task.created",
        ),
    )
    event = result.scalar_one()
    assert event.category == AuditCategory.DOMAIN.value
    assert event.actor_type == AuditActorType.TELEGRAM.value
