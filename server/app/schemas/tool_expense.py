from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

CurrencyCode = Literal["USD", "EUR", "PLN", "BYN"]


class ExchangeRatesResponse(BaseModel):
    base: str
    rates: dict[str, str]
    updated_at: str | None
    provider: str


class ExpenseParseRequest(BaseModel):
    text: str = Field(min_length=1, max_length=500)
    default_currency: CurrencyCode | None = None


class ExpenseParseResponse(BaseModel):
    valid: bool
    amount: Decimal | None = None
    currency: CurrencyCode | None = None
    category: str | None = None
    tool_name: str | None = None
    expense_date: date | None = None
    error: str | None = None


class ToolExpenseCreate(BaseModel):
    tool_name: str = Field(min_length=1, max_length=255)
    amount: Decimal = Field(gt=0, decimal_places=2)
    currency: CurrencyCode = "USD"
    expense_date: date
    category: str | None = Field(None, max_length=64)
    notes: str | None = None


class ToolExpenseUpdate(BaseModel):
    tool_name: str | None = Field(None, min_length=1, max_length=255)
    amount: Decimal | None = Field(None, gt=0, decimal_places=2)
    currency: CurrencyCode | None = None
    expense_date: date | None = None
    category: str | None = Field(None, max_length=64)
    notes: str | None = None


class ToolExpenseResponse(BaseModel):
    id: int
    tool_name: str
    amount: Decimal
    currency: str
    expense_date: date
    category: str | None
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ToolExpenseMonthTotal(BaseModel):
    period: str
    total: Decimal


class ToolExpenseToolTotal(BaseModel):
    tool_name: str
    total: Decimal


class ToolExpenseCategoryTotal(BaseModel):
    category: str
    total: Decimal


class ToolExpenseSummary(BaseModel):
    total: Decimal
    currency: str
    rates_updated_at: str | None = None
    by_month: list[ToolExpenseMonthTotal]
    by_tool: list[ToolExpenseToolTotal]
    by_category: list[ToolExpenseCategoryTotal]
