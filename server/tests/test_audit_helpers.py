from datetime import UTC, datetime

import pytest

from app.db.documents.audit import (
    AuditActorType,
    AuditCategory,
    AuditSource,
)
from app.db.registry import DatabaseRegistry
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
async def test_create_task_records_domain_audit(registry: DatabaseRegistry) -> None:
    svc = TaskService(registry)
    task = await svc.create_task(
        telegram_user_id=123456789,
        title="Audit test",
        scheduled_at=datetime(2026, 6, 1, 10, 0, tzinfo=UTC),
    )

    row = await registry.mongo_db.audit_events.find_one(
        {
            "resource_type": "task",
            "resource_id": task.id,
            "action": "task.created",
        },
    )
    assert row is not None
    assert row["category"] == AuditCategory.DOMAIN.value
    assert row["actor_type"] == AuditActorType.TELEGRAM.value
