"""Backward-compatible shim for expense category schemas."""

from app.schemas.expense_category import (
    ExpenseCategoryCreate,
    ExpenseCategoryResponse,
    ExpenseCategoryUpdate,
)

__all__ = ["ExpenseCategoryCreate", "ExpenseCategoryResponse", "ExpenseCategoryUpdate"]
