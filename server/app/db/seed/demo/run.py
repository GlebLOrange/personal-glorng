"""Demo seed orchestrator: bulk random data per platform tool."""

from app.core.logging import logger
from app.db.init_service import DatabaseInitService
from app.db.registry import DatabaseRegistry
from app.db.seed.core.admin import WEAK_PASSWORDS
from app.db.seed.demo.reset import reset_tool_tables
from app.db.seed.demo.tools.expenses import seed_demo_expenses
from app.db.seed.demo.tools.feedback import seed_demo_feedback
from app.db.seed.demo.tools.recipes import seed_demo_recipes
from app.db.seed.demo.tools.tasks import seed_demo_tasks
from app.db.seed.demo.tools.urls import seed_demo_short_urls
from app.db.seed.demo.users import seed_demo_users
from app.settings import get_settings

DEMO_TELEGRAM_USER_ID = 123456789


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
                await seed_demo_users(registry, settings)
                logger.info(
                    "Demo seed skipped: tool data already present",
                    context={"recipes": existing},
                )
                return

        if reset:
            await reset_tool_tables(registry)

        admin, reader, writer = await seed_demo_users(registry, settings)
        owners = [admin, reader, writer]

        recipe_count = await seed_demo_recipes(registry, count)
        expense_count = await seed_demo_expenses(registry, count)
        task_count = await seed_demo_tasks(
            registry,
            count,
            telegram_user_id=telegram_user_id,
            timezone=settings.TIMEZONE,
            actor_id=admin.id,
        )
        feedback_count = await seed_demo_feedback(registry, count)
        url_count = await seed_demo_short_urls(registry, count, owners)
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
