from app.core.catalogs import DEFAULT_EXPENSE_CATEGORY, DEFAULT_EXPENSE_CATEGORY_NAMES
from app.core.exceptions import NotFoundError, ValidationError
from app.db.documents.expense import ExpenseCategory
from app.db.registry import DatabaseRegistry
from app.schemas.expense_category import (
    ExpenseCategoryCreate,
    ExpenseCategoryDelete,
    ExpenseCategoryResponse,
    ExpenseCategoryUpdate,
)

DEFAULT_CATEGORY = DEFAULT_EXPENSE_CATEGORY
DEFAULT_CATEGORY_NAMES = DEFAULT_EXPENSE_CATEGORY_NAMES
_DEFAULT_CATEGORY_NAMES = DEFAULT_EXPENSE_CATEGORY_NAMES


class ExpenseCategoryService:
    def __init__(self, registry: DatabaseRegistry) -> None:
        self.registry = registry

    def _expenses(self):
        if self.registry.expenses is None:
            msg = "Expense repository is not initialized"
            raise RuntimeError(msg)
        return self.registry.expenses

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

        existing = await self._expenses().find_category_by_name(normalized)
        if existing is not None:
            return

        sort_order = await self._expenses().next_category_sort_order()
        category = ExpenseCategory(name=normalized, sort_order=sort_order)
        await self._expenses().categories.insert(category)

    async def ensure_defaults(self) -> None:
        """Seed starter categories once; never reinsert after the marker is set."""
        if await self._expenses().categories_defaults_seeded():
            return

        existing_rows = await self._expenses().categories.list(limit=500)
        existing = {row.name.lower() for row in existing_rows}
        next_order = await self._expenses().next_category_sort_order()
        for name in _DEFAULT_CATEGORY_NAMES:
            if name.lower() in existing:
                continue
            await self._expenses().categories.insert(
                ExpenseCategory(name=name, sort_order=next_order),
            )
            next_order += 1
            existing.add(name.lower())
        await self._expenses().mark_categories_defaults_seeded()

    async def list_categories(self) -> list[ExpenseCategoryResponse]:
        # One-time starter seed only; never reinserts after the seeded marker is set.
        await self.ensure_defaults()
        rows = await self._expenses().categories.list(
            limit=500,
            sort=[("sort_order", 1), ("name", 1)],
        )
        return [ExpenseCategoryResponse.model_validate(row) for row in rows]

    async def list_names(self) -> list[str]:
        categories = await self.list_categories()
        return [category.name for category in categories]

    async def get(self, category_id: int) -> ExpenseCategory:
        row = await self._expenses().categories.get_or_none(category_id)
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

        existing = await self._expenses().find_category_by_name(name)
        if existing is not None:
            raise ValidationError("Category already exists")

        sort_order = await self._expenses().next_category_sort_order()
        row = ExpenseCategory(name=name, sort_order=sort_order)
        row = await self._expenses().categories.insert(row)
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
            existing = await self._expenses().find_category_by_name(new_name)
            if existing is not None and existing.id != category_id:
                raise ValidationError("Category already exists")

            old_name = row.name
            await self._expenses().rename_category_on_expenses(old_name, new_name)
            row = await self._expenses().categories.update_fields(
                category_id,
                name=new_name,
            )

        payload = data.model_dump(exclude_unset=True)
        if "monthly_budget" in payload:
            row = await self._expenses().categories.update_fields(
                category_id,
                monthly_budget=payload["monthly_budget"],
            )

        return ExpenseCategoryResponse.model_validate(row)

    async def delete_category(
        self,
        category_id: int,
        replacement: ExpenseCategoryDelete | None = None,
    ) -> None:
        """Delete a category; reassign in-use expenses when replacement is provided."""
        row = await self.get(category_id)
        in_use = await self._expenses().count_expenses_in_category(row.name)
        if in_use == 0:
            await self._expenses().categories.delete(category_id)
            return

        if replacement is None:
            raise ValidationError(
                "Category is used by expenses; provide replacement_category_id",
            )

        if replacement.replacement_category_id == category_id:
            raise ValidationError("Cannot reassign a category to itself")

        if replacement.replacement_category_id is None:
            await self._expenses().reassign_category_on_expenses(row.name, None)
        else:
            target = await self.get(replacement.replacement_category_id)
            await self._expenses().reassign_category_on_expenses(row.name, target.name)

        await self._expenses().categories.delete(category_id)
