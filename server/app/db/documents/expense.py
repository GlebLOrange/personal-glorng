from datetime import date, datetime
from decimal import Decimal

from pydantic import field_validator

from app.db.documents.base import TimestampedDocument


class Expense(TimestampedDocument):
    tool_name: str
    amount: Decimal
    currency: str = "PLN"
    expense_date: date
    category: str | None = None
    notes: str | None = None
    source: str = "web_admin"

    @field_validator("expense_date", mode="before")
    @classmethod
    def _coerce_expense_date(cls, value: object) -> date:
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, str):
            return date.fromisoformat(value)
        if isinstance(value, date):
            return value
        msg = f"Unsupported expense_date value: {value!r}"
        raise TypeError(msg)

    @field_validator("amount", mode="before")
    @classmethod
    def _coerce_amount(cls, value: object) -> Decimal:
        if isinstance(value, str):
            return Decimal(value)
        if isinstance(value, Decimal):
            return value
        if isinstance(value, int | float):
            return Decimal(str(value))
        msg = f"Unsupported amount value: {value!r}"
        raise TypeError(msg)


class ExpenseCategory(TimestampedDocument):
    name: str
    sort_order: int = 0
    monthly_budget: Decimal | None = None

    @field_validator("monthly_budget", mode="before")
    @classmethod
    def _coerce_monthly_budget(cls, value: object) -> Decimal | None:
        if value is None:
            return None
        if isinstance(value, str):
            return Decimal(value)
        if isinstance(value, Decimal):
            return value
        if isinstance(value, int | float):
            return Decimal(str(value))
        msg = f"Unsupported monthly_budget value: {value!r}"
        raise TypeError(msg)
