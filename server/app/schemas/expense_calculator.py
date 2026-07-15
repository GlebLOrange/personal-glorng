"""Schemas for the public expense calculator tool."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator

from app.core.catalogs import DEFAULT_EXPENSE_CURRENCY, CurrencyCode
from app.schemas.validators import validate_clean_optional, validate_clean_required

MAX_LINE_ITEMS = 50
MAX_BUDGET_ROWS = 20


class ExpenseCalculatorLineItem(BaseModel):
    """Single row in the itemized sum mode."""

    label: str = Field(default="", max_length=120)
    amount: Decimal = Field(ge=0, decimal_places=2)
    currency: CurrencyCode | None = None

    @field_validator("label")
    @classmethod
    def clean_label(cls, value: str) -> str:
        return validate_clean_optional(value, max_length=120) or ""


class ExpenseCalculatorBudgetRow(BaseModel):
    """Budget category row for budget / what-if modes."""

    name: str = Field(min_length=1, max_length=64)
    budget: Decimal = Field(ge=0, decimal_places=2)
    spent: Decimal = Field(ge=0, decimal_places=2, default=Decimal("0"))

    @field_validator("name")
    @classmethod
    def clean_name(cls, value: str) -> str:
        return validate_clean_required(value, max_length=64, field_name="Category name")


class ExpenseCalculatorState(BaseModel):
    """Persisted calculator snapshot (superuser only)."""

    display_currency: CurrencyCode = DEFAULT_EXPENSE_CURRENCY
    line_items: list[ExpenseCalculatorLineItem] = Field(default_factory=list)
    budget_rows: list[ExpenseCalculatorBudgetRow] = Field(default_factory=list)
    saved_at: datetime | None = None

    @field_validator("line_items")
    @classmethod
    def cap_line_items(
        cls,
        value: list[ExpenseCalculatorLineItem],
    ) -> list[ExpenseCalculatorLineItem]:
        if len(value) > MAX_LINE_ITEMS:
            msg = f"At most {MAX_LINE_ITEMS} line items allowed"
            raise ValueError(msg)
        return value

    @field_validator("budget_rows")
    @classmethod
    def cap_budget_rows(
        cls,
        value: list[ExpenseCalculatorBudgetRow],
    ) -> list[ExpenseCalculatorBudgetRow]:
        if len(value) > MAX_BUDGET_ROWS:
            msg = f"At most {MAX_BUDGET_ROWS} budget rows allowed"
            raise ValueError(msg)
        return value
