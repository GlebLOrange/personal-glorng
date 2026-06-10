"""Backward-compatible shim for expense category SQLAlchemy model."""

from app.db.models.expense_category import ExpenseCategory as ToolExpenseCategory

__all__ = ["ToolExpenseCategory"]
