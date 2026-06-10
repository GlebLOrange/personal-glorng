"""Core dev seed orchestrator (admin + sample data)."""

from app.db.init_service import DatabaseInitService
from app.db.registry import DatabaseRegistry
from app.db.seed.core.admin import WEAK_PASSWORDS, seed_admin
from app.db.seed.core.expenses import seed_expense_categories, seed_expenses
from app.db.seed.core.recipes import seed_recipes
from app.db.seed.core.tasks import seed_tasks
from app.settings import get_settings


async def seed() -> None:
    """Seed admin user and sample tool data for local development."""
    settings = get_settings()
    if not settings.SEED_PASSWORD or settings.SEED_PASSWORD.lower() in WEAK_PASSWORDS:
        raise RuntimeError("SEED_PASSWORD env var missing or too weak")

    registry = DatabaseRegistry()
    init_svc = DatabaseInitService(registry, settings)
    try:
        await init_svc.startup()
        owner = await seed_admin(registry, settings)
        await seed_recipes(registry)
        await seed_expense_categories(registry)
        await seed_expenses(registry)
        await seed_tasks(registry, settings, owner)
    finally:
        await init_svc.shutdown()
