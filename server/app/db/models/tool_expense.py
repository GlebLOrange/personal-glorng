"""Backward-compatible shim for expense SQLAlchemy model."""

from app.db.models.expense import Expense as ToolExpense

__all__ = ["ToolExpense"]
