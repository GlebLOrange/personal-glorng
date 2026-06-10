"""Backward-compatible shim for expense API schemas."""

from app.schemas.expense import (
    ExpenseCatalogResponse,
    ExpenseCategoryTotal as ToolExpenseCategoryTotal,
    ExpenseCreate as ToolExpenseCreate,
    ExpenseMonthTotal as ToolExpenseMonthTotal,
    ExpenseParseRequest,
    ExpenseParseResponse,
    ExpenseResponse as ToolExpenseResponse,
    ExpenseSummary as ToolExpenseSummary,
    ExpenseToolTotal as ToolExpenseToolTotal,
    ExpenseUpdate as ToolExpenseUpdate,
    ExchangeRatesResponse,
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
