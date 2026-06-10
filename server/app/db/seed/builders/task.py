"""Factories for task seed data."""

import random
from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

from app.db.documents.task import Task, TaskStatus

TASK_TITLES = (
    "Review PR",
    "Call dentist",
    "Buy groceries",
    "Write blog post",
    "Sync calendar",
    "Pay invoices",
    "Gym session",
    "Fix nginx config",
    "Reply to feedback",
    "Plan sprint",
)


def build_tasks_for_today(
    count: int,
    *,
    telegram_user_id: int,
    timezone: str,
    seed: int = 42,
) -> list[Task]:
    """Build tasks scheduled between start and end of today in the given timezone."""
    rng = random.Random(seed)  # noqa: S311
    tz = ZoneInfo(timezone)
    now_local = datetime.now(tz)
    start = now_local.replace(hour=0, minute=0, second=0, microsecond=0)
    end = now_local.replace(hour=23, minute=59, second=59, microsecond=0)
    span_seconds = int((end - start).total_seconds())

    rows: list[Task] = []
    statuses = [TaskStatus.PENDING] * 20 + [
        TaskStatus.COMPLETED,
        TaskStatus.POSTPONED,
        TaskStatus.NOT_COMPLETED,
    ]
    for _ in range(count):
        offset = rng.randint(0, max(span_seconds, 1))
        scheduled = start + timedelta(seconds=offset)
        rows.append(
            Task(
                telegram_user_id=telegram_user_id,
                title=rng.choice(TASK_TITLES),
                description=None,
                location=None,
                scheduled_at=scheduled.astimezone(UTC),
                status=rng.choice(statuses),
            ),
        )
    return rows
