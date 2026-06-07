import json
from pathlib import Path

from app.core.catalogs import (
    ALLOWED_CURRENCIES,
    DEFAULT_EXPENSE_CATEGORY,
    DEFAULT_EXPENSE_CATEGORY_NAMES,
    DEFAULT_EXPENSE_CURRENCY,
    EXCHANGE_RATE_TARGETS,
)

_CATALOG_PATH = (
    Path(__file__).resolve().parents[2] / "shared" / "expense_catalog.json"
)


def test_expense_catalog_matches_shared_fixture() -> None:
    fixture = json.loads(_CATALOG_PATH.read_text(encoding="utf-8"))
    assert list(ALLOWED_CURRENCIES) == fixture["currencies"]
    assert DEFAULT_EXPENSE_CURRENCY == fixture["default_currency"]
    assert list(EXCHANGE_RATE_TARGETS) == fixture["exchange_rate_targets"]
    assert list(DEFAULT_EXPENSE_CATEGORY_NAMES) == fixture["categories"]
    assert DEFAULT_EXPENSE_CATEGORY == fixture["default_category"]
