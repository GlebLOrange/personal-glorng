"""Factories for expense seed data."""

import random
from datetime import date, timedelta
from decimal import Decimal

from app.core.catalogs import (
    ALLOWED_CURRENCIES,
    DEFAULT_EXPENSE_CATEGORY_NAMES,
)
from app.db.documents.expense import Expense

EXPENSE_VENDORS = (
    "Cursor",
    "Vercel",
    "Railway",
    "OpenAI",
    "Groq",
    "GitHub",
    "Cloudflare",
    "Hetzner",
)
# Backward-compatible alias
EXPENSE_TOOLS = EXPENSE_VENDORS

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


def build_random_expenses(count: int, *, seed: int = 42) -> list[Expense]:
    """Build expense rows spread over the last three months."""
    rng = random.Random(seed)  # noqa: S311
    today = date.today()
    rows: list[Expense] = []
    for _ in range(count):
        days_ago = rng.randint(0, 90)
        rows.append(
            Expense(
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
