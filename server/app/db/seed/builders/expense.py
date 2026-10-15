"""Factories for expense seed data."""

from __future__ import annotations

import random
from collections.abc import Iterable, Mapping
from datetime import date, timedelta
from decimal import Decimal

from app.core.catalogs import (
    ALLOWED_CURRENCIES,
    DEFAULT_EXPENSE_CATEGORY_NAMES,
)
from app.db.documents.expense import Expense

# merchant, category, amount range in grosze (PLN cents)
EXPENSE_MERCHANTS: tuple[tuple[str, str, int, int], ...] = (
    ("Biedronka", "Food", 1500, 12000),
    ("Lidl", "Food", 2000, 15000),
    ("Żabka", "Food", 500, 4000),
    ("Rent", "Home & bills", 150000, 350000),
    ("Utilities", "Home & bills", 15000, 45000),
    ("Internet", "Home & bills", 5000, 12000),
    ("Bolt", "Transport", 800, 4500),
    ("PKP", "Transport", 1500, 8000),
    ("Fuel", "Transport", 10000, 35000),
    ("Pharmacy", "Health", 1500, 12000),
    ("Dentist", "Health", 15000, 40000),
    ("Gym", "Personal", 8000, 20000),
    ("Haircut", "Personal", 4000, 12000),
    ("Cinema", "Entertainment", 3000, 8000),
    ("Spotify", "Entertainment", 1999, 2999),
    ("Amazon", "Other", 2000, 25000),
    ("Cursor", "Other", 2000, 20000),
)

EXPENSE_NOTES = (
    "Weekly shop",
    "Shared with roommate",
    "Work expense",
    "Subscription",
    "Cash payment",
    "Online order",
)

FOREIGN_CURRENCIES = ("EUR", "USD", "BYN")

SEED_CATEGORY_BUDGETS: dict[str, Decimal] = {
    "Food": Decimal("1200.00"),
    "Home & bills": Decimal("2500.00"),
    "Transport": Decimal("400.00"),
    "Health": Decimal("200.00"),
    "Personal": Decimal("300.00"),
    "Entertainment": Decimal("250.00"),
    "Other": Decimal("150.00"),
}

EXPENSE_CATEGORIES = DEFAULT_EXPENSE_CATEGORY_NAMES
EXPENSE_CURRENCIES = ALLOWED_CURRENCIES
EXPENSE_PRODUCTS = tuple(merchant for merchant, _, _, _ in EXPENSE_MERCHANTS)
EXPENSE_VENDORS = EXPENSE_PRODUCTS


def budgets_for_empty_categories(
    categories: Iterable[tuple[str, Decimal | None]],
    *,
    budgets: Mapping[str, Decimal] | None = None,
) -> list[tuple[str, Decimal]]:
    """Return ``(name, budget)`` for categories that still have no monthly budget."""
    mapping = budgets if budgets is not None else SEED_CATEGORY_BUDGETS
    updates: list[tuple[str, Decimal]] = []
    for name, current in categories:
        if current is not None:
            continue
        budget = mapping.get(name)
        if budget is not None:
            updates.append((name, budget))
    return updates


def build_random_expenses(count: int, *, seed: int = 42) -> list[Expense]:
    """Build category-matched expense rows biased toward the current month."""
    rng = random.Random(seed)  # noqa: S311
    today = date.today()
    rows: list[Expense] = []
    for _ in range(count):
        merchant, category, lo, hi = rng.choice(EXPENSE_MERCHANTS)
        # ~70% of dates fall in the last 30 days for the current-month dashboard.
        days_ago = rng.randint(0, 29) if rng.random() < 0.7 else rng.randint(30, 90)
        currency = "PLN" if rng.random() < 0.9 else rng.choice(FOREIGN_CURRENCIES)
        notes = rng.choice(EXPENSE_NOTES) if rng.random() < 0.5 else None
        amount = Decimal(rng.randint(lo, hi)) / Decimal(100)
        rows.append(
            Expense(
                tool_name=merchant,
                amount=amount.quantize(Decimal("0.01")),
                currency=currency,
                expense_date=today - timedelta(days=days_ago),
                category=category,
                notes=notes,
            ),
        )
    return rows
