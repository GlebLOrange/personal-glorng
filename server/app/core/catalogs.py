"""Shared product catalogs consumed by API, services, and parity tests."""

import json
from pathlib import Path
from typing import Literal, cast

CurrencyCode = Literal["PLN", "EUR", "USD", "BYN"]

_CATALOG_PATH = Path(__file__).resolve().parents[3] / "shared" / "expense_catalog.json"


def _load_expense_catalog() -> dict[str, object]:
    """Load currencies/categories from the repo-shared fixture."""
    return json.loads(_CATALOG_PATH.read_text(encoding="utf-8"))


_catalog = _load_expense_catalog()

ALLOWED_CURRENCIES: tuple[CurrencyCode, ...] = tuple(
    cast(list[CurrencyCode], _catalog["currencies"])
)
DEFAULT_EXPENSE_CURRENCY = cast(CurrencyCode, _catalog["default_currency"])
EXCHANGE_RATE_TARGETS: tuple[CurrencyCode, ...] = tuple(
    cast(list[CurrencyCode], _catalog["exchange_rate_targets"])
)

DEFAULT_EXPENSE_CATEGORY = str(_catalog["default_category"])
DEFAULT_EXPENSE_CATEGORY_NAMES: tuple[str, ...] = tuple(
    cast(list[str], _catalog["categories"])
)
