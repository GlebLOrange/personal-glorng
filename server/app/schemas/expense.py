from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.catalogs import DEFAULT_EXPENSE_CURRENCY, CurrencyCode
from app.schemas.common import PaginatedResponse
from app.schemas.validators import validate_clean_optional, validate_clean_required


class ExpenseCatalogResponse(BaseModel):
    currencies: list[str]
    default_currency: str
    exchange_rate_targets: list[str]
    categories: list[str]
    default_category: str


class ExchangeRatesResponse(BaseModel):
    base: str
    rates: dict[str, str]
    updated_at: str | None
    provider: str


class ExpenseParseRequest(BaseModel):
    text: str = Field(min_length=1, max_length=500)
    default_currency: CurrencyCode | None = None

    @field_validator("text")
    @classmethod
    def clean_text(cls, value: str) -> str:
        return validate_clean_required(value, max_length=500, field_name="Text")


class ExpenseParseResponse(BaseModel):
    valid: bool
    amount: Decimal | None = None
    currency: CurrencyCode | None = None
    category: str | None = None
    tool_name: str | None = None
    expense_date: date | None = None
    error: str | None = None


class ExpenseCreate(BaseModel):
    tool_name: str = Field(min_length=1, max_length=255)
    amount: Decimal = Field(gt=0, decimal_places=2)
    currency: CurrencyCode = DEFAULT_EXPENSE_CURRENCY
    expense_date: date = Field(description="Expense date (YYYY-MM-DD).")
    category: str | None = Field(None, max_length=64)
    notes: str | None = Field(None, max_length=5000)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "tool_name": "OpenAI API",
                "amount": "12.50",
                "currency": "USD",
                "expense_date": "2026-06-01",
                "category": "AI",
                "notes": "June usage",
            }
        }
    )

    @field_validator("tool_name")
    @classmethod
    def clean_tool_name(cls, value: str) -> str:
        return validate_clean_required(value, max_length=255, field_name="Tool name")

    @field_validator("category")
    @classmethod
    def clean_category(cls, value: str | None) -> str | None:
        return validate_clean_optional(value, max_length=64)

    @field_validator("notes")
    @classmethod
    def clean_notes(cls, value: str | None) -> str | None:
        return validate_clean_optional(value, max_length=5000)


class ExpenseUpdate(BaseModel):
    tool_name: str | None = Field(None, min_length=1, max_length=255)
    amount: Decimal | None = Field(None, gt=0, decimal_places=2)
    currency: CurrencyCode | None = None
    expense_date: date | None = Field(
        None,
        description="Expense date (YYYY-MM-DD).",
    )
    category: str | None = Field(None, max_length=64)
    notes: str | None = Field(None, max_length=5000)

    @field_validator("tool_name")
    @classmethod
    def clean_tool_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return validate_clean_required(value, max_length=255, field_name="Tool name")

    @field_validator("category")
    @classmethod
    def clean_category(cls, value: str | None) -> str | None:
        return validate_clean_optional(value, max_length=64)

    @field_validator("notes")
    @classmethod
    def clean_notes(cls, value: str | None) -> str | None:
        return validate_clean_optional(value, max_length=5000)


class ExpenseResponse(BaseModel):
    id: int
    tool_name: str
    amount: Decimal
    currency: str
    expense_date: date = Field(description="Expense date (YYYY-MM-DD).")
    category: str | None
    notes: str | None
    source: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ExpenseListResponse(PaginatedResponse[ExpenseResponse]):
    pass


class ExpenseMonthTotal(BaseModel):
    period: str
    total: Decimal


class ExpenseToolTotal(BaseModel):
    tool_name: str
    total: Decimal


class ExpenseCategoryTotal(BaseModel):
    category: str
    total: Decimal


class ExpenseSummary(BaseModel):
    total: Decimal
    currency: str
    rates_updated_at: str | None = None
    by_month: list[ExpenseMonthTotal]
    by_tool: list[ExpenseToolTotal]
    by_category: list[ExpenseCategoryTotal]
