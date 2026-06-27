"""Backward-compatible shim for expense API schemas."""

from app.schemas.expense import (
    ExchangeRatesResponse,
    ExpenseCatalogResponse,
    ExpenseParseRequest,
    ExpenseParseResponse,
)
from app.schemas.expense import (
    ExpenseCategoryTotal as ToolExpenseCategoryTotal,
)
from app.schemas.expense import (
    ExpenseCreate as ToolExpenseCreate,
)
from app.schemas.expense import (
    ExpenseMonthTotal as ToolExpenseMonthTotal,
)
from app.schemas.expense import (
    ExpenseResponse as ToolExpenseResponse,
)
from app.schemas.expense import (
    ExpenseSummary as ToolExpenseSummary,
)
from app.schemas.expense import (
    ExpenseToolTotal as ToolExpenseToolTotal,
)
from app.schemas.expense import (
    ExpenseUpdate as ToolExpenseUpdate,
)

__all__ = [
    "ExchangeRatesResponse",
    "ExpenseCatalogResponse",
    "ExpenseParseRequest",
    "ExpenseParseResponse",
    "ToolExpenseCategoryTotal",
    "ToolExpenseCreate",
    "ToolExpenseMonthTotal",
    "ToolExpenseResponse",
    "ToolExpenseSummary",
    "ToolExpenseToolTotal",
    "ToolExpenseUpdate",
]
