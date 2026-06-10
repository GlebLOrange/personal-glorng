"""Rule-based parsing for quick expense messages from Telegram."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from zoneinfo import ZoneInfo

from app.core.catalogs import DEFAULT_EXPENSE_CATEGORY
from app.services.currency import ALLOWED_CURRENCIES
from app.settings import get_settings

_AMOUNT_RE = re.compile(r"^\s*(\d+(?:[.,]\d{1,2})?)\s*(.*)$", re.DOTALL)

_CURRENCY_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\b(?:pln|zł|zl)\b", re.IGNORECASE), "PLN"),
    (re.compile(r"\b(?:usd|\$)\b", re.IGNORECASE), "USD"),
    (re.compile(r"\b(?:eur|€)\b", re.IGNORECASE), "EUR"),
    (re.compile(r"\b(?:byn)\b", re.IGNORECASE), "BYN"),
)

_CATEGORY_KEYWORDS: dict[str, tuple[str, ...]] = {
    "Groceries": (
        "groceries",
        "grocery",
        "biedronka",
        "lidl",
        "żabka",
        "zabka",
        "carrefour",
        "aldi",
        "food",
        "restaurant",
        "lunch",
        "dinner",
        "breakfast",
        "cafe",
        "coffee",
        "pizza",
    ),
    "Home": (
        "home",
        "rent",
        "housing",
        "bills",
        "utilities",
        "internet",
        "electric",
        "insurance",
    ),
    "Transport": (
        "transport",
        "parking",
        "uber",
        "bolt",
        "taxi",
        "bus",
        "train",
        "gas",
        "fuel",
        "shell",
        "orlen",
        "bp",
        "petrol",
    ),
}

DEFAULT_CATEGORY = DEFAULT_EXPENSE_CATEGORY


@dataclass(frozen=True)
class ParsedExpense:
    """Parsed expense fields ready for ExpenseCreate."""

    amount: Decimal
    currency: str
    category: str
    tool_name: str
    expense_date: date
    parse_error: str | None = None

    @property
    def is_valid(self) -> bool:
        return self.parse_error is None and self.amount > 0


def today_in_tz() -> date:
    """Return today's date in the configured timezone."""
    settings = get_settings()
    return datetime.now(ZoneInfo(settings.TIMEZONE)).date()


def _normalize_amount(raw: str) -> Decimal:
    return Decimal(raw.replace(",", ".")).quantize(Decimal("0.01"))


def _detect_currency(text: str, default: str) -> tuple[str, str]:
    for pattern, code in _CURRENCY_PATTERNS:
        if pattern.search(text):
            cleaned = pattern.sub(" ", text)
            return code, " ".join(cleaned.split())
    return default, text.strip()


def _find_category_keyword(text: str) -> tuple[str, str | None]:
    best_category: str | None = None
    best_keyword: str | None = None
    for category, keywords in _CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            pattern = re.compile(rf"\b{re.escape(keyword)}\b", re.IGNORECASE)
            if not pattern.search(text):
                continue
            if best_keyword is None or len(keyword) > len(best_keyword):
                best_category = category
                best_keyword = keyword
    if best_category is None:
        return DEFAULT_CATEGORY, None
    return best_category, best_keyword


def _remove_keyword(text: str, keyword: str) -> str:
    pattern = re.compile(rf"\b{re.escape(keyword)}\b", re.IGNORECASE)
    return " ".join(pattern.sub(" ", text).split())


def _title_description(text: str) -> str:
    stripped = text.strip()
    if not stripped:
        return ""
    return stripped[0].upper() + stripped[1:]


def parse_expense_text(
    text: str,
    *,
    default_currency: str | None = None,
    expense_date: date | None = None,
) -> ParsedExpense:
    """Parse a one-line expense message into structured fields."""
    settings = get_settings()
    currency_default = default_currency or settings.EXPENSE_DEFAULT_CURRENCY
    if currency_default not in ALLOWED_CURRENCIES:
        currency_default = "PLN"
    when = expense_date or today_in_tz()

    cleaned = text.strip()
    if not cleaned:
        return ParsedExpense(
            amount=Decimal("0"),
            currency=currency_default,
            category=DEFAULT_CATEGORY,
            tool_name="",
            expense_date=when,
            parse_error="Message is empty",
        )

    match = _AMOUNT_RE.match(cleaned)
    if not match:
        return ParsedExpense(
            amount=Decimal("0"),
            currency=currency_default,
            category=DEFAULT_CATEGORY,
            tool_name="",
            expense_date=when,
            parse_error="Start with an amount, e.g. 45 groceries",
        )

    raw_amount, remainder = match.group(1), match.group(2).strip()
    try:
        amount = _normalize_amount(raw_amount)
    except InvalidOperation:
        return ParsedExpense(
            amount=Decimal("0"),
            currency=currency_default,
            category=DEFAULT_CATEGORY,
            tool_name="",
            expense_date=when,
            parse_error="Invalid amount",
        )

    if amount <= 0:
        return ParsedExpense(
            amount=amount,
            currency=currency_default,
            category=DEFAULT_CATEGORY,
            tool_name="",
            expense_date=when,
            parse_error="Amount must be greater than zero",
        )

    currency, after_currency = _detect_currency(remainder, currency_default)
    category, keyword = _find_category_keyword(after_currency)
    description = (
        _remove_keyword(after_currency, keyword) if keyword else after_currency.strip()
    )
    tool_name = _title_description(description)
    if not tool_name:
        tool_name = _title_description(keyword) if keyword else category

    return ParsedExpense(
        amount=amount,
        currency=currency,
        category=category,
        tool_name=tool_name,
        expense_date=when,
    )
