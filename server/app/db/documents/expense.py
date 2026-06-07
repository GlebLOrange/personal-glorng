from datetime import date
from decimal import Decimal

from app.db.documents.base import TimestampedDocument


class ToolExpense(TimestampedDocument):
    tool_name: str
    amount: Decimal
    currency: str = "PLN"
    expense_date: date
    category: str | None = None
    notes: str | None = None
    source: str = "web_admin"


class ToolExpenseCategory(TimestampedDocument):
    name: str
    sort_order: int = 0
    monthly_budget: Decimal | None = None
