"""Factories for deterministic dev seed data."""

import random
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

from app.core.catalogs import (
    ALLOWED_CURRENCIES,
    DEFAULT_EXPENSE_CATEGORY_NAMES,
)
from app.db.models.task import Task, TaskStatus
from app.db.models.tool_expense import ToolExpense

EXPENSE_TOOLS = (
    "Cursor",
    "Vercel",
    "Railway",
    "OpenAI",
    "Groq",
    "GitHub",
    "Cloudflare",
    "Hetzner",
)
EXPENSE_CATEGORIES = DEFAULT_EXPENSE_CATEGORY_NAMES
EXPENSE_PRODUCTS = (
    "Groceries run",
    "Rent",
    "Bus ticket",
    "Fuel",
    "Utilities",
    "Biedronka",
    "Pharmacy",
)
EXPENSE_CURRENCIES = ALLOWED_CURRENCIES
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


def build_random_expenses(count: int, *, seed: int = 42) -> list[ToolExpense]:
    """Build expense rows spread over the last three months."""
    rng = random.Random(seed)  # noqa: S311
    today = date.today()
    rows: list[ToolExpense] = []
    for _ in range(count):
        days_ago = rng.randint(0, 90)
        rows.append(
            ToolExpense(
                tool_name=rng.choice(EXPENSE_PRODUCTS),
                amount=Decimal(str(rng.randint(500, 20000) / 100)).quantize(
                    Decimal("0.01"),
                ),
                currency=rng.choice(EXPENSE_CURRENCIES),
                expense_date=today - timedelta(days=days_ago),
                category=rng.choice(EXPENSE_CATEGORIES),
                notes=None,
            ),
        )
    return rows


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
