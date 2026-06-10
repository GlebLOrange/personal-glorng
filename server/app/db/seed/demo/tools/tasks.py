"""Demo task seeding."""

from app.db.documents.audit import AuditActorType, AuditSource
from app.db.documents.task import TaskStatus
from app.db.registry import DatabaseRegistry
from app.db.seed.builders.demo import build_random_tasks
from app.services.task import TaskService


async def seed_demo_tasks(
    registry: DatabaseRegistry,
    count: int,
    *,
    telegram_user_id: int,
    timezone: str,
    actor_id: int | None,
) -> int:
    """Insert tasks via TaskService for audit coverage."""
    svc = TaskService(registry)
    created = 0
    for built in build_random_tasks(
        count,
        telegram_user_id=telegram_user_id,
        timezone=timezone,
        seed=99,
    ):
        task = await svc.create_task(
            telegram_user_id=built.telegram_user_id,
            title=built.title,
            scheduled_at=built.scheduled_at,
            description=built.description,
            location=built.location,
            source=AuditSource.WEB_ADMIN,
            actor_type=AuditActorType.USER,
            actor_id=actor_id,
        )
        if built.status != TaskStatus.PENDING:
            await svc.update_task_status(
                task=task,
                new_status=built.status,
                actor_type=AuditActorType.USER,
                actor_id=actor_id,
                source=AuditSource.WEB_ADMIN,
            )
        created += 1
    return created
