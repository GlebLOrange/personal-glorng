"""Backward-compatible shim for expense service."""

from app.services.expense import ExpenseService as ToolExpenseService

__all__ = ["ToolExpenseService"]
