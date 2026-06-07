"""Demo seed: bulk random data for each platform tool."""

from app.core.logging import logger
from app.db.documents.audit import AuditActorType, AuditSource
from app.db.documents.task import TaskStatus
from app.db.documents.user import User
from app.db.init_service import DatabaseInitService
from app.db.registry import DatabaseRegistry
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
from app.services.task import TaskService
from app.services.tool_expense_category import ToolExpenseCategoryService
from app.services.url import UrlService
from app.services.user import create_user, get_user_by_email
from app.settings import Settings, get_settings

DEMO_TELEGRAM_USER_ID = 123456789
DEMO_USER_EMAILS = (DEMO_READER_EMAIL, DEMO_WRITER_EMAIL)

_TASK_COLLECTIONS = (
    "reminders",
    "task_status_history",
    "google_sync_queue",
    "task_intakes",
    "tasks",
)


async def _reset_tool_tables(registry: DatabaseRegistry) -> None:
    """Remove demo tool rows in dependency-safe order."""
    mongo = registry.require_mongo()
    for name in _TASK_COLLECTIONS:
        await mongo[name].delete_many({})

    if registry.urls is not None:
        await registry.urls._col().delete_many({})
    if registry.feedback is not None:
        await registry.feedback._col().delete_many({})
    if registry.expenses is not None:
        await registry.expenses.expenses._col().delete_many({})
    if registry.recipes is not None:
        await registry.recipes._col().delete_many({})

    if registry.users is not None:
        for email in DEMO_USER_EMAILS:
            user = await get_user_by_email(registry, email)
            if user is not None:
                await registry.users.delete(user.id)

    logger.info("Demo tool tables reset")


async def _ensure_demo_user(
    registry: DatabaseRegistry,
    *,
    email: str,
    password: str,
    permissions: list[str],
) -> User:
    """Create a demo user when missing."""
    existing = await get_user_by_email(registry, email)
    if existing:
        logger.info("Demo user already exists", context={"email": email})
        return existing
    user = await create_user(
        registry,
        email=email,
        password=password,
        permissions=permissions,
        is_verified=True,
        is_protected=False,
    )
    logger.info("Demo user created", context={"email": email})
    return user


async def _seed_demo_users(
    registry: DatabaseRegistry,
    settings: Settings,
) -> tuple[User, User, User]:
    """Ensure admin plus two capability-based demo users."""
    admin = await _seed_admin(registry, settings)
    if admin is None:
        msg = "Failed to seed admin user"
        raise RuntimeError(msg)
    reader = await _ensure_demo_user(
        registry,
        email=DEMO_READER_EMAIL,
        password=settings.SEED_PASSWORD,
        permissions=demo_reader_permissions(),
    )
    writer = await _ensure_demo_user(
        registry,
        email=DEMO_WRITER_EMAIL,
        password=settings.SEED_PASSWORD,
        permissions=demo_writer_permissions(),
    )
    return admin, reader, writer


async def _seed_recipes(registry: DatabaseRegistry, count: int) -> int:
    """Insert procedurally generated recipes."""
    if registry.recipes is None:
        msg = "Recipes repository is not initialized"
        raise RuntimeError(msg)

    tag_pool = build_recipe_tag_pool(count)
    recipes = build_random_recipes(count, tag_pool)
    for recipe in recipes:
        await registry.recipes.insert(recipe)
    return len(recipes)


async def _seed_expenses(registry: DatabaseRegistry, count: int) -> int:
    """Insert random expenses and ensure default categories."""
    if registry.expenses is None:
        msg = "Expense repository is not initialized"
        raise RuntimeError(msg)

    svc = ToolExpenseCategoryService(registry)
    await svc.ensure_defaults()
    expenses = build_random_expenses(count, seed=99)
    for expense in expenses:
        await registry.expenses.expenses.insert(expense)
    return len(expenses)


async def _seed_tasks(
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


async def _seed_feedback(registry: DatabaseRegistry, count: int) -> int:
    """Insert random feedback rows."""
    if registry.feedback is None:
        msg = "Feedback repository is not initialized"
        raise RuntimeError(msg)

    rows = build_random_feedback(count, seed=99)
    for row in rows:
        await registry.feedback.insert(row)
    return len(rows)


async def _seed_short_urls(
    registry: DatabaseRegistry,
    count: int,
    owners: list[User],
) -> int:
    """Insert short URLs owned round-robin across demo users."""
    if registry.urls is None:
        msg = "URL repository is not initialized"
        raise RuntimeError(msg)

    svc = UrlService(registry)
    created = 0
    for index, seed in enumerate(build_short_url_seeds(count, seed=99)):
        owner = owners[index % len(owners)]
        url = await svc.create_short_url(
            original_url=seed.original_url,
            created_by=owner.id,
            title=seed.title,
        )
        if seed.clicks:
            await registry.urls.update_fields(url.id, clicks=seed.clicks)
        created += 1
    return created


async def seed_demo(
    *,
    count: int = 50,
    reset: bool = True,
    skip_if_populated: bool = False,
) -> None:
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

    registry = DatabaseRegistry()
    init_svc = DatabaseInitService(registry, settings)
    try:
        await init_svc.startup()
        if skip_if_populated and registry.recipes is not None:
            existing = await registry.recipes.count()
            if existing > 0:
                await _seed_demo_users(registry, settings)
                logger.info(
                    "Demo seed skipped: tool data already present",
                    context={"recipes": existing},
                )
                return

        if reset:
            await _reset_tool_tables(registry)

        admin, reader, writer = await _seed_demo_users(registry, settings)
        owners = [admin, reader, writer]

        recipe_count = await _seed_recipes(registry, count)
        expense_count = await _seed_expenses(registry, count)
        task_count = await _seed_tasks(
            registry,
            count,
            telegram_user_id=telegram_user_id,
            timezone=settings.TIMEZONE,
            actor_id=admin.id,
        )
        feedback_count = await _seed_feedback(registry, count)
        url_count = await _seed_short_urls(registry, count, owners)
    finally:
        await init_svc.shutdown()

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
