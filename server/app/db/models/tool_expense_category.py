from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, BaseModelMixin


class ToolExpenseCategory(BaseModelMixin, Base):
    __tablename__ = "tool_expense_categories"

    name: Mapped[str] = mapped_column(String(64), unique=True)
    sort_order: Mapped[int] = mapped_column(Integer, server_default="0")
