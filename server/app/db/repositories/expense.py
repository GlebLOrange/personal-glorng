import re
from datetime import UTC, date, datetime
from decimal import Decimal
from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.documents.expense import Expense, ExpenseCategory
from app.db.repositories.base import MongoRepository, _parse_doc

EXPENSE_SORTS: dict[str, list[tuple[str, int]]] = {
    "date_asc": [("expense_date", 1), ("created_at", 1)],
    "date_desc": [("expense_date", -1), ("created_at", -1)],
    "category_asc": [("category", 1), ("expense_date", -1), ("created_at", -1)],
    "category_desc": [("category", -1), ("expense_date", -1), ("created_at", -1)],
    "product_asc": [("tool_name", 1), ("expense_date", -1), ("created_at", -1)],
    "product_desc": [("tool_name", -1), ("expense_date", -1), ("created_at", -1)],
    "amount_asc": [("amount", 1), ("expense_date", -1), ("created_at", -1)],
    "amount_desc": [("amount", -1), ("expense_date", -1), ("created_at", -1)],
}


def _decimal_from_mongo(value: object) -> Decimal:
    if hasattr(value, "to_decimal"):
        return value.to_decimal()
    return Decimal(str(value))


class ExpenseRepository:
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.expenses = MongoRepository(db, "expenses", Expense)
        self.categories = MongoRepository(db, "expense_categories", ExpenseCategory)

    async def find_category_by_name(self, name: str) -> ExpenseCategory | None:
        data = await self.categories._col().find_one(
            {"name": {"$regex": f"^{re.escape(name)}$", "$options": "i"}},
        )
        if data is None:
            return None
        return _parse_doc(ExpenseCategory, data)

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
        when = datetime.combine(
            value, datetime.max.time() if end_of_day else datetime.min.time()
        )
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
        offset: int = 0,
        limit: int | None = None,
        sort: str = "date_desc",
    ) -> list[Expense]:
        query = self._expense_query(
            date_from=date_from,
            date_to=date_to,
            tool_name=tool_name,
            category=category,
        )
        sort_spec = EXPENSE_SORTS.get(sort, EXPENSE_SORTS["date_desc"])
        cursor = self.expenses._col().find(query).sort(sort_spec).skip(offset)
        if limit is not None:
            cursor = cursor.limit(limit)
        return [_parse_doc(Expense, row) async for row in cursor]

    async def count_expenses(
        self,
        *,
        date_from: date | None = None,
        date_to: date | None = None,
        tool_name: str | None = None,
        category: str | None = None,
    ) -> int:
        query = self._expense_query(
            date_from=date_from,
            date_to=date_to,
            tool_name=tool_name,
            category=category,
        )
        return await self.expenses._col().count_documents(query)

    async def summarize_expenses(
        self,
        *,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> dict[str, list[dict[str, Any]]]:
        query = self._expense_query(date_from=date_from, date_to=date_to)
        pipeline: list[dict[str, Any]] = [
            {"$match": query},
            {
                "$facet": {
                    "total": [
                        {
                            "$group": {
                                "_id": {"currency": "$currency"},
                                "amount": {"$sum": {"$toDecimal": "$amount"}},
                            },
                        },
                    ],
                    "by_month": [
                        {
                            "$group": {
                                "_id": {
                                    "period": {
                                        "$dateToString": {
                                            "format": "%Y-%m",
                                            "date": "$expense_date",
                                        },
                                    },
                                    "currency": "$currency",
                                },
                                "amount": {"$sum": {"$toDecimal": "$amount"}},
                            },
                        },
                        {"$sort": {"_id.period": 1}},
                    ],
                    "by_tool": [
                        {
                            "$group": {
                                "_id": {
                                    "tool_name": "$tool_name",
                                    "currency": "$currency",
                                },
                                "amount": {"$sum": {"$toDecimal": "$amount"}},
                            },
                        },
                    ],
                    "by_category": [
                        {
                            "$group": {
                                "_id": {
                                    "category": {
                                        "$ifNull": ["$category", "Uncategorized"],
                                    },
                                    "currency": "$currency",
                                },
                                "amount": {"$sum": {"$toDecimal": "$amount"}},
                            },
                        },
                    ],
                },
            },
        ]
        rows = await self.expenses._col().aggregate(pipeline).to_list(length=1)
        if not rows:
            return {"total": [], "by_month": [], "by_tool": [], "by_category": []}
        summary = rows[0]
        for bucket in ("total", "by_month", "by_tool", "by_category"):
            for row in summary.get(bucket, []):
                row["amount"] = _decimal_from_mongo(row["amount"])
        return summary
