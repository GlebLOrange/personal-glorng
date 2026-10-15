"""Unit tests for expense seed factories (no DB)."""

from datetime import date, timedelta
from decimal import Decimal

from app.db.seed.builders.expense import (
    EXPENSE_MERCHANTS,
    budgets_for_empty_categories,
    build_random_expenses,
)

_MERCHANT_CATEGORY = {merchant: category for merchant, category, _, _ in EXPENSE_MERCHANTS}


def test_build_random_expenses_matches_merchant_category() -> None:
    """Each seeded expense uses the category that belongs to its merchant."""
    rows = build_random_expenses(50, seed=7)
    assert len(rows) == 50
    today = date.today()
    pln_count = 0
    with_notes = 0
    for row in rows:
        assert row.category == _MERCHANT_CATEGORY[row.tool_name]
        assert today - timedelta(days=90) <= row.expense_date <= today
        if row.currency == "PLN":
            pln_count += 1
        if row.notes is not None:
            with_notes += 1
    assert pln_count >= 40
    assert with_notes >= 1


def test_budgets_for_empty_categories_skips_existing() -> None:
    """Budget fill only targets categories that still have no monthly budget."""
    updates = budgets_for_empty_categories(
        [
            ("Food", None),
            ("Transport", Decimal("500.00")),
            ("Health", None),
            ("Custom", None),
        ],
    )
    by_name = dict(updates)
    assert by_name["Food"] == Decimal("1200.00")
    assert by_name["Health"] == Decimal("200.00")
    assert "Transport" not in by_name
    assert "Custom" not in by_name
