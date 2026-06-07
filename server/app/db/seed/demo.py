"""Demo seed: bulk random data for each platform tool."""

from sqlalchemy import delete, select, update

from app.core.logging import logger
from app.db.models.audit_event import AuditActorType, AuditSource
from app.db.models.feedback import Feedback
from app.db.models.google_sync_queue import GoogleSyncQueue
from app.db.models.recipe import Recipe
from app.db.models.reminder import Reminder
from app.db.models.task import Task, TaskStatus
from app.db.models.task_intake import TaskIntake
from app.db.models.task_status_history import TaskStatusHistory
from app.db.models.tool_expense import ToolExpense
from app.db.models.url import ShortenedUrl
from app.db.models.user import User
from app.db.seed.builders import build_random_expenses
from app.db.seed.demo_builders import (
    DEMO_READER_EMAIL,
    DEMO_WRITER_EMAIL,
    build_random_feedback,
    build_random_recipes,
    build_random_tasks,
    build_recipe_tag_pool,
    build_short_url_seeds,
    demo_reader_permissions,
    demo_writer_permissions,
)
from app.db.seed.run import WEAK_PASSWORDS, _seed_admin
from app.db.session import get_session_factory
from app.services.task import TaskService
from app.services.tool_expense_category import ToolExpenseCategoryService
from app.services.url import UrlService
from app.services.user import create_user
from app.settings import get_settings

DEMO_TELEGRAM_USER_ID = 123456789
DEMO_USER_EMAILS = (DEMO_READER_EMAIL, DEMO_WRITER_EMAIL)


async def _reset_tool_tables(db) -> None:  # noqa: ANN001
    """Remove demo tool rows in FK-safe order."""
    for model in (
        Reminder,
        TaskStatusHistory,
        GoogleSyncQueue,
        TaskIntake,
        Task,
        ShortenedUrl,
        Feedback,
        ToolExpense,
        Recipe,
    ):
        await db.execute(delete(model))
    await db.execute(delete(User).where(User.email.in_(DEMO_USER_EMAILS)))
    await db.flush()
    logger.info("Demo tool tables reset")


async def _ensure_demo_user(
    db,  # noqa: ANN001
    *,
    email: str,
    password: str,
    permissions: list[str],
) -> User:
    """Create a demo user when missing."""
    result = await db.execute(select(User).where(User.email == email))
    existing = result.scalar_one_or_none()
    if existing:
        logger.info("Demo user already exists", context={"email": email})
        return existing
    user = await create_user(
        db,
        email=email,
        password=password,
        permissions=permissions,
        is_verified=True,
        is_protected=False,
    )
    logger.info("Demo user created", context={"email": email})
    return user


async def _seed_demo_users(db, settings) -> tuple[User, User, User]:  # noqa: ANN001
    """Ensure admin plus two capability-based demo users."""
    admin = await _seed_admin(db, settings)
    if admin is None:
        msg = "Failed to seed admin user"
        raise RuntimeError(msg)
    reader = await _ensure_demo_user(
        db,
        email=DEMO_READER_EMAIL,
        password=settings.SEED_PASSWORD,
        permissions=demo_reader_permissions(),
    )
    writer = await _ensure_demo_user(
        db,
        email=DEMO_WRITER_EMAIL,
        password=settings.SEED_PASSWORD,
        permissions=demo_writer_permissions(),
    )
    return admin, reader, writer


async def _seed_recipes(db, count: int) -> int:  # noqa: ANN001
    """Insert procedurally generated recipes."""
    tag_pool = build_recipe_tag_pool(count)
    recipes = build_random_recipes(count, tag_pool)
    for recipe in recipes:
        db.add(recipe)
    await db.flush()
    return len(recipes)


async def _seed_expenses(db, count: int) -> int:  # noqa: ANN001
    """Insert random expenses and ensure default categories."""
    svc = ToolExpenseCategoryService(db)
    await svc.ensure_defaults()
    expenses = build_random_expenses(count, seed=99)
    for expense in expenses:
        db.add(expense)
    await db.flush()
    return len(expenses)


async def _seed_tasks(
    db,  # noqa: ANN001
    count: int,
    *,
    telegram_user_id: int,
    timezone: str,
    actor_id: int | None,
) -> int:
    """Insert tasks via TaskService for audit coverage."""
    svc = TaskService(db)
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
            task.status = built.status
            await db.flush()
        created += 1
    return created


async def _seed_feedback(db, count: int) -> int:  # noqa: ANN001
    """Insert random feedback rows."""
    rows = build_random_feedback(count, seed=99)
    for row in rows:
        db.add(row)
    await db.flush()
    return len(rows)


async def _seed_short_urls(
    db,  # noqa: ANN001
    count: int,
    owners: list[User],
) -> int:
    """Insert short URLs owned round-robin across demo users."""
    svc = UrlService(db)
    created = 0
    for index, seed in enumerate(build_short_url_seeds(count, seed=99)):
        owner = owners[index % len(owners)]
        url = await svc.create_short_url(
            original_url=seed.original_url,
            created_by=owner.id,
            title=seed.title,
        )
        if seed.clicks:
            await db.execute(
                update(ShortenedUrl)
                .where(ShortenedUrl.id == url.id)
                .values(clicks=seed.clicks),
            )
        created += 1
    await db.flush()
    return created


async def seed_demo(*, count: int = 50, reset: bool = True) -> None:
    """Fill the database with random demo data for each tool."""
    settings = get_settings()
    if not settings.SEED_PASSWORD or settings.SEED_PASSWORD.lower() in WEAK_PASSWORDS:
        raise RuntimeError("SEED_PASSWORD env var missing or too weak")

    telegram_user_id = settings.TELEGRAM_ALLOWED_USER_ID or DEMO_TELEGRAM_USER_ID
    if not settings.TELEGRAM_ALLOWED_USER_ID:
        logger.warning(
            "TELEGRAM_ALLOWED_USER_ID not set; using demo fallback",
            context={"telegram_user_id": telegram_user_id},
        )

    async with get_session_factory()() as db:
        if reset:
            await _reset_tool_tables(db)

        admin, reader, writer = await _seed_demo_users(db, settings)
        owners = [admin, reader, writer]

        recipe_count = await _seed_recipes(db, count)
        expense_count = await _seed_expenses(db, count)
        task_count = await _seed_tasks(
            db,
            count,
            telegram_user_id=telegram_user_id,
            timezone=settings.TIMEZONE,
            actor_id=admin.id,
        )
        feedback_count = await _seed_feedback(db, count)
        url_count = await _seed_short_urls(db, count, owners)

        await db.commit()

    logger.info(
        "Demo seed complete",
        context={
            "reset": reset,
            "count": count,
            "recipes": recipe_count,
            "expenses": expense_count,
            "tasks": task_count,
            "feedback": feedback_count,
            "short_urls": url_count,
            "users": len(owners),
        },
    )
