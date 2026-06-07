"""Shared product catalogs consumed by API, services, and parity tests."""

from typing import Literal

CurrencyCode = Literal["PLN", "EUR", "USD", "BYN"]

ALLOWED_CURRENCIES: tuple[CurrencyCode, ...] = ("PLN", "EUR", "USD", "BYN")
DEFAULT_EXPENSE_CURRENCY: CurrencyCode = "PLN"
EXCHANGE_RATE_TARGETS: tuple[CurrencyCode, ...] = ("EUR", "USD", "BYN")

DEFAULT_EXPENSE_CATEGORY = "Groceries"
DEFAULT_EXPENSE_CATEGORY_NAMES: tuple[str, ...] = ("Groceries", "Home", "Transport")
