"""Sample expense seeding for core dev seed."""

from app.core.logging import logger
from app.db.registry import DatabaseRegistry
from app.db.seed.builders.expense import build_random_expenses
from app.db.seed.core.admin import require_repos
from app.services.expense_category import ExpenseCategoryService


async def seed_expense_categories(registry: DatabaseRegistry) -> None:
    """Ensure default expense categories exist."""
    svc = ExpenseCategoryService(registry)
    await svc.ensure_defaults()
    names = await svc.list_names()
    logger.info("Expense categories ready", context={"categories": names})


async def seed_expenses(registry: DatabaseRegistry) -> None:
    """Insert sample expenses when the collection is empty."""
    require_repos(registry)
    count = await registry.expenses.expenses.count()
    if count:
        logger.info("Expenses already seeded", context={"count": count})
        return

    for expense in build_random_expenses(25):
        await registry.expenses.expenses.insert(expense)
    logger.info("Seeded sample expenses", context={"count": 25})
