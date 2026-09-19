"""Unified DB seed: mock test data for platform tools."""

from app.core.logging import logger
from app.db.init_service import DatabaseInitService
from app.db.registry import DatabaseRegistry
from app.db.seed.cli.multicooker import seed_multicooker_recipes
from app.db.seed.core.admin import WEAK_PASSWORDS
from app.db.seed.demo.reset import reset_tool_tables
from app.db.seed.demo.tools.expenses import seed_demo_expenses
from app.db.seed.demo.tools.feedback import seed_demo_feedback
from app.db.seed.demo.tools.news import seed_demo_news
from app.db.seed.demo.tools.recipes import seed_demo_recipes
from app.db.seed.demo.tools.tasks import seed_demo_tasks
from app.db.seed.demo.tools.urls import seed_demo_short_urls
from app.db.seed.demo.users import seed_demo_users
from app.settings import get_settings

DEMO_TELEGRAM_USER_ID = 123456789

# Fixed mock volumes for make seed-db / RUN_SEED.
SEED_DEMO_RECIPES = 100
SEED_MULTICOOKER_RECIPES = 100
SEED_EXPENSES = 100
SEED_TASKS = 100
SEED_NEWS = 20
SEED_SHORT_URLS = 50
SEED_FEEDBACK = 50


async def seed_demo(
    *,
    reset: bool = True,
    skip_if_populated: bool = False,
) -> None:
    """Fill the database with fixed-volume mock data for each tool."""
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
    recipe_count = 0
    multicooker_count = 0
    expense_count = 0
    task_count = 0
    feedback_count = 0
    url_count = 0
    news_count = 0
    owner_count = 0
    try:
        await init_svc.startup()
        if skip_if_populated and registry.recipes is not None:
            existing = await registry.recipes.count()
            if existing > 0:
                await seed_demo_users(registry, settings)
                logger.info(
                    "Seed skipped: tool data already present",
                    context={"recipes": existing},
                )
                return

        if reset:
            await reset_tool_tables(registry)

        admin, reader, writer = await seed_demo_users(registry, settings)
        owners = [admin, reader, writer]
        owner_count = len(owners)

        recipe_count = await seed_demo_recipes(registry, SEED_DEMO_RECIPES)
        multicooker_count = await seed_multicooker_recipes(
            registry,
            SEED_MULTICOOKER_RECIPES,
        )
        expense_count = await seed_demo_expenses(registry, SEED_EXPENSES)
        task_count = await seed_demo_tasks(
            registry,
            SEED_TASKS,
            telegram_user_id=telegram_user_id,
            timezone=settings.TIMEZONE,
            actor_id=admin.id,
        )
        feedback_count = await seed_demo_feedback(registry, SEED_FEEDBACK)
        url_count = await seed_demo_short_urls(registry, SEED_SHORT_URLS, owners)
        news_count = await seed_demo_news(registry, SEED_NEWS)
    finally:
        await init_svc.shutdown()

    logger.info(
        "Database seed complete",
        context={
            "reset": reset,
            "recipes": recipe_count,
            "multicooker_recipes": multicooker_count,
            "expenses": expense_count,
            "tasks": task_count,
            "feedback": feedback_count,
            "short_urls": url_count,
            "news": news_count,
            "users": owner_count,
        },
    )
