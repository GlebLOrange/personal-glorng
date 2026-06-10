"""Sample task seeding for core dev seed."""

from app.core.logging import logger
from app.db.documents.audit import AuditActorType, AuditSource
from app.db.documents.user import User
from app.db.registry import DatabaseRegistry
from app.db.seed.builders.task import build_tasks_for_today
from app.services.task import TaskService
from app.settings import Settings


async def seed_tasks(
    registry: DatabaseRegistry,
    settings: Settings,
    owner: User | None,
) -> None:
    """Insert sample tasks for today when the collection is empty."""
    if registry.tasks is None:
        msg = "Tasks repository is not initialized"
        raise RuntimeError(msg)

    count = await registry.tasks.count()
    if count:
        logger.info("Tasks already seeded", context={"count": count})
        return

    telegram_user_id = settings.TELEGRAM_ALLOWED_USER_ID
    if not telegram_user_id:
        logger.warning("Skipping task seed: TELEGRAM_ALLOWED_USER_ID not set")
        return

    svc = TaskService(registry)
    actor_id = owner.id if owner else None
    for task in build_tasks_for_today(
        25,
        telegram_user_id=telegram_user_id,
        timezone=settings.TIMEZONE,
    ):
        await svc.create_task(
            telegram_user_id=task.telegram_user_id,
            title=task.title,
            scheduled_at=task.scheduled_at,
            description=task.description,
            location=task.location,
            source=AuditSource.WEB_ADMIN,
            actor_type=AuditActorType.USER,
            actor_id=actor_id,
        )
    logger.info("Seeded sample tasks", context={"count": 25})
