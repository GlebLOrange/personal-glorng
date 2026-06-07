import re
from datetime import UTC, date, datetime
from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.documents.expense import ToolExpense, ToolExpenseCategory
from app.db.repositories.base import MongoRepository, _parse_doc


class ExpenseRepository:
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.expenses = MongoRepository(db, "tool_expenses", ToolExpense)
        self.categories = MongoRepository(
            db, "tool_expense_categories", ToolExpenseCategory
        )

    async def find_category_by_name(self, name: str) -> ToolExpenseCategory | None:
        data = await self.categories._col().find_one(
            {"name": {"$regex": f"^{re.escape(name)}$", "$options": "i"}},
        )
        if data is None:
            return None
        return _parse_doc(ToolExpenseCategory, data)

    async def next_category_sort_order(self) -> int:
        doc = await self.categories._col().find_one(
            {},
            sort=[("sort_order", -1)],
            projection={"sort_order": 1},
        )
        if doc is None:
            return 0
        return int(doc.get("sort_order", -1)) + 1

    async def list_category_names(self) -> list[str]:
        rows = await self.categories.list(
            limit=500, sort=[("sort_order", 1), ("name", 1)]
        )
        return [row.name for row in rows]

    async def count_expenses_in_category(self, category_name: str) -> int:
        return await self.expenses.count(category=category_name)

    async def rename_category_on_expenses(self, old_name: str, new_name: str) -> None:
        await self.expenses._col().update_many(
            {"category": old_name},
            {"$set": {"category": new_name}},
        )

    @staticmethod
    def _date_bound(value: date, *, end_of_day: bool = False) -> datetime:
        when = datetime.combine(value, datetime.max.time() if end_of_day else datetime.min.time())
        return when.replace(tzinfo=UTC)

    def _expense_query(
        self,
        *,
        date_from: date | None = None,
        date_to: date | None = None,
        tool_name: str | None = None,
        category: str | None = None,
    ) -> dict[str, Any]:
        query: dict[str, Any] = {}
        if date_from is not None or date_to is not None:
            date_filter: dict[str, Any] = {}
            if date_from is not None:
                date_filter["$gte"] = self._date_bound(date_from)
            if date_to is not None:
                date_filter["$lte"] = self._date_bound(date_to, end_of_day=True)
            query["expense_date"] = date_filter
        if tool_name:
            query["tool_name"] = {"$regex": re.escape(tool_name), "$options": "i"}
        if category:
            query["category"] = {"$regex": re.escape(category), "$options": "i"}
        return query

    async def list_expenses(
        self,
        *,
        date_from: date | None = None,
        date_to: date | None = None,
        tool_name: str | None = None,
        category: str | None = None,
    ) -> list[ToolExpense]:
        query = self._expense_query(
            date_from=date_from,
            date_to=date_to,
            tool_name=tool_name,
            category=category,
        )
        cursor = (
            self.expenses._col()
            .find(query)
            .sort([("expense_date", -1), ("created_at", -1)])
        )
        return [_parse_doc(ToolExpense, row) async for row in cursor]
