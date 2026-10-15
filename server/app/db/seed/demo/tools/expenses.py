"""Demo expense seeding."""

from app.db.registry import DatabaseRegistry
from app.db.seed.builders.expense import (
    budgets_for_empty_categories,
    build_random_expenses,
)
from app.services.expense_category import ExpenseCategoryService


async def seed_demo_expenses(registry: DatabaseRegistry, count: int) -> int:
    """Insert realistic expenses and fill empty category monthly budgets."""
    if registry.expenses is None:
        msg = "Expense repository is not initialized"
        raise RuntimeError(msg)

    svc = ExpenseCategoryService(registry)
    await svc.ensure_defaults()

    category_rows = await registry.expenses.categories.list(limit=500)
    by_name = {row.name: row for row in category_rows}
    for name, budget in budgets_for_empty_categories(
        ((row.name, row.monthly_budget) for row in category_rows),
    ):
        category = by_name[name]
        await registry.expenses.categories.update_fields(
            category.id,
            monthly_budget=budget,
        )

    expenses = build_random_expenses(count, seed=99)
    for expense in expenses:
        await registry.expenses.expenses.insert(expense)
    return len(expenses)
