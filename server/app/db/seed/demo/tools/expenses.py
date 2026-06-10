"""Demo expense seeding."""

from app.db.registry import DatabaseRegistry
from app.db.seed.builders.expense import build_random_expenses
from app.services.expense_category import ExpenseCategoryService


async def seed_demo_expenses(registry: DatabaseRegistry, count: int) -> int:
    """Insert random expenses and ensure default categories."""
    if registry.expenses is None:
        msg = "Expense repository is not initialized"
        raise RuntimeError(msg)

    svc = ExpenseCategoryService(registry)
    await svc.ensure_defaults()
    expenses = build_random_expenses(count, seed=99)
    for expense in expenses:
        await registry.expenses.expenses.insert(expense)
    return len(expenses)
