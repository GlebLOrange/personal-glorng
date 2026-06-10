"""Backward-compatible shim for expense category service."""

from app.services.expense_category import ExpenseCategoryService as ToolExpenseCategoryService

__all__ = ["ToolExpenseCategoryService"]
