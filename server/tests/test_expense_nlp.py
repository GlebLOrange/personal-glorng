from datetime import date
from decimal import Decimal

import pytest

from app.todobot.utils import expense_nlp


@pytest.fixture
def fixed_date(monkeypatch: pytest.MonkeyPatch) -> date:
    target = date(2026, 3, 15)

    def _today() -> date:
        return target

    monkeypatch.setattr(expense_nlp, "today_in_tz", _today)
    return target


def test_parse_polish_decimal_comma(fixed_date: date) -> None:
    parsed = expense_nlp.parse_expense_text("89,50 biedronka", expense_date=fixed_date)
    assert parsed.is_valid
    assert parsed.amount == Decimal("89.50")
    assert parsed.currency == "PLN"
    assert parsed.category == "Groceries"
    assert parsed.tool_name == "Biedronka"


def test_parse_food_keyword(fixed_date: date) -> None:
    parsed = expense_nlp.parse_expense_text("120 food", expense_date=fixed_date)
    assert parsed.is_valid
    assert parsed.category == "Groceries"
    assert parsed.tool_name == "Food"


def test_parse_eur_currency_override(fixed_date: date) -> None:
    parsed = expense_nlp.parse_expense_text("50 EUR lunch", expense_date=fixed_date)
    assert parsed.is_valid
    assert parsed.amount == Decimal("50.00")
    assert parsed.currency == "EUR"
    assert parsed.category == "Groceries"


def test_parse_gas_keyword(fixed_date: date) -> None:
    parsed = expense_nlp.parse_expense_text("200 shell", expense_date=fixed_date)
    assert parsed.is_valid
    assert parsed.category == "Transport"
    assert parsed.tool_name == "Shell"


def test_parse_default_groceries_without_keyword(fixed_date: date) -> None:
    parsed = expense_nlp.parse_expense_text("45.00 zakupy", expense_date=fixed_date)
    assert parsed.is_valid
    assert parsed.category == "Groceries"
    assert parsed.tool_name == "Zakupy"


def test_parse_invalid_amount(fixed_date: date) -> None:
    parsed = expense_nlp.parse_expense_text("abc food", expense_date=fixed_date)
    assert not parsed.is_valid
    assert parsed.parse_error is not None


def test_parse_groceries_keyword(fixed_date: date) -> None:
    parsed = expense_nlp.parse_expense_text("45 groceries", expense_date=fixed_date)
    assert parsed.is_valid
    assert parsed.category == "Groceries"
    assert parsed.amount == Decimal("45.00")
