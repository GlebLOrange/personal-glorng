from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ValidationError
from app.db.models.tool_expense import ToolExpense
from app.db.models.tool_expense_category import ToolExpenseCategory
from app.schemas.tool_expense_category import (
    ExpenseCategoryCreate,
    ExpenseCategoryResponse,
    ExpenseCategoryUpdate,
)

DEFAULT_CATEGORY = "Groceries"
DEFAULT_CATEGORY_NAMES: tuple[str, ...] = ("Groceries", "Home", "Transport")
_DEFAULT_CATEGORY_NAMES = DEFAULT_CATEGORY_NAMES


class ToolExpenseCategoryService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    @staticmethod
    def normalize_name(name: str) -> str:
        return " ".join(name.strip().split())

    async def ensure_category(self, name: str | None) -> None:
        """Create category row when saving an expense with a new category name."""
        if name is None:
            return
        normalized = self.normalize_name(name)
        if not normalized:
            return

        existing = await self.db.execute(
            select(ToolExpenseCategory.id).where(
                func.lower(ToolExpenseCategory.name) == normalized.lower(),
            ),
        )
        if existing.scalar_one_or_none() is not None:
            return

        max_order = await self.db.execute(
            select(func.coalesce(func.max(ToolExpenseCategory.sort_order), -1)),
        )
        next_order = int(max_order.scalar_one()) + 1
        self.db.add(ToolExpenseCategory(name=normalized, sort_order=next_order))
        await self.db.flush()

    async def ensure_defaults(self) -> None:
        result = await self.db.execute(select(ToolExpenseCategory.name))
        existing = {row[0].lower() for row in result}
        max_order_result = await self.db.execute(
            select(func.coalesce(func.max(ToolExpenseCategory.sort_order), -1)),
        )
        next_order = int(max_order_result.scalar_one()) + 1
        for name in _DEFAULT_CATEGORY_NAMES:
            if name.lower() in existing:
                continue
            self.db.add(ToolExpenseCategory(name=name, sort_order=next_order))
            next_order += 1
            existing.add(name.lower())
        await self.db.flush()

    async def list_categories(self) -> list[ExpenseCategoryResponse]:
        await self.ensure_defaults()
        result = await self.db.execute(
            select(ToolExpenseCategory).order_by(
                ToolExpenseCategory.sort_order,
                ToolExpenseCategory.name,
            ),
        )
        return [
            ExpenseCategoryResponse.model_validate(row)
            for row in result.scalars().all()
        ]

    async def list_names(self) -> list[str]:
        categories = await self.list_categories()
        return [category.name for category in categories]

    async def get(self, category_id: int) -> ToolExpenseCategory:
        result = await self.db.execute(
            select(ToolExpenseCategory).where(ToolExpenseCategory.id == category_id),
        )
        row = result.scalar_one_or_none()
        if row is None:
            raise NotFoundError("Category not found")
        return row

    async def create_category(
        self,
        data: ExpenseCategoryCreate,
    ) -> ExpenseCategoryResponse:
        name = self.normalize_name(data.name)
        if not name:
            raise ValidationError("Category name is required")

        existing = await self.db.execute(
            select(ToolExpenseCategory.id).where(
                func.lower(ToolExpenseCategory.name) == name.lower(),
            ),
        )
        if existing.scalar_one_or_none() is not None:
            raise ValidationError("Category already exists")

        max_order = await self.db.execute(
            select(func.coalesce(func.max(ToolExpenseCategory.sort_order), -1)),
        )
        next_order = int(max_order.scalar_one()) + 1

        row = ToolExpenseCategory(name=name, sort_order=next_order)
        self.db.add(row)
        await self.db.flush()
        await self.db.refresh(row)
        return ExpenseCategoryResponse.model_validate(row)

    async def update_category(
        self,
        category_id: int,
        data: ExpenseCategoryUpdate,
    ) -> ExpenseCategoryResponse:
        row = await self.get(category_id)
        new_name = self.normalize_name(data.name)
        if not new_name:
            raise ValidationError("Category name is required")

        if new_name.lower() != row.name.lower():
            existing = await self.db.execute(
                select(ToolExpenseCategory.id).where(
                    func.lower(ToolExpenseCategory.name) == new_name.lower(),
                    ToolExpenseCategory.id != category_id,
                ),
            )
            if existing.scalar_one_or_none() is not None:
                raise ValidationError("Category already exists")

            old_name = row.name
            row.name = new_name
            await self.db.execute(
                update(ToolExpense)
                .where(ToolExpense.category == old_name)
                .values(category=new_name),
            )

        payload = data.model_dump(exclude_unset=True)
        if "monthly_budget" in payload:
            row.monthly_budget = payload["monthly_budget"]

        await self.db.flush()
        await self.db.refresh(row)
        return ExpenseCategoryResponse.model_validate(row)

    async def delete_category(self, category_id: int) -> None:
        row = await self.get(category_id)
        in_use = await self.db.execute(
            select(func.count())
            .select_from(ToolExpense)
            .where(ToolExpense.category == row.name),
        )
        if int(in_use.scalar_one()) > 0:
            raise ValidationError(
                "Category is used by expenses; reassign or delete those expenses first",
            )
        await self.db.delete(row)
