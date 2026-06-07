import csv
import io
from calendar import monthrange
from collections import defaultdict
from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ValidationError
from app.db.models.audit_event import AuditActorType, AuditSource
from app.db.models.tool_expense import ToolExpense
from app.schemas.tool_expense import (
    ToolExpenseCategoryTotal,
    ToolExpenseCreate,
    ToolExpenseMonthTotal,
    ToolExpenseResponse,
    ToolExpenseSummary,
    ToolExpenseToolTotal,
    ToolExpenseUpdate,
)
from app.services.audit import AuditService
from app.services.base import CRUDService
from app.core.catalogs import ALLOWED_CURRENCIES, DEFAULT_EXPENSE_CURRENCY
from app.services.currency import CurrencyService
from app.services.search_indexers.expense import index_expense, remove_expense
from app.services.tool_expense_category import ToolExpenseCategoryService

_CSV_FORMULA_PREFIXES = frozenset("=+-@\t\r")


def _csv_cell(value: str) -> str:
    """Prefix spreadsheet formula triggers to prevent CSV injection."""
    if value and value[0] in _CSV_FORMULA_PREFIXES:
        return f"'{value}"
    return value


class ToolExpenseService(CRUDService[ToolExpense]):
    def __init__(
        self,
        db: AsyncSession,
        *,
        currency_svc: CurrencyService | None = None,
    ) -> None:
        super().__init__(db, ToolExpense)
        self._currency_svc = currency_svc or CurrencyService()

    @staticmethod
    def month_date_bounds(month: str) -> tuple[date, date]:
        """Return inclusive calendar bounds for YYYY-MM."""
        parts = month.split("-", 1)
        if len(parts) != 2:
            raise ValidationError("month must be YYYY-MM")
        try:
            year, mon = int(parts[0]), int(parts[1])
        except ValueError as exc:
            raise ValidationError("month must be YYYY-MM") from exc
        if not 1 <= mon <= 12:
            raise ValidationError("month must be YYYY-MM")
        last_day = monthrange(year, mon)[1]
        return date(year, mon, 1), date(year, mon, last_day)

    @staticmethod
    def _to_response(expense: ToolExpense) -> ToolExpenseResponse:
        return ToolExpenseResponse.model_validate(expense)

    def _apply_filters(
        self,
        query: select,
        date_from: date | None = None,
        date_to: date | None = None,
        tool_name: str | None = None,
        category: str | None = None,
    ) -> select:
        if date_from is not None:
            query = query.where(ToolExpense.expense_date >= date_from)
        if date_to is not None:
            query = query.where(ToolExpense.expense_date <= date_to)
        if tool_name:
            query = query.where(ToolExpense.tool_name.ilike(f"%{tool_name}%"))
        if category:
            query = query.where(ToolExpense.category.ilike(f"%{category}%"))
        return query

    async def create_expense(
        self,
        data: ToolExpenseCreate,
        *,
        source: AuditSource = AuditSource.WEB_ADMIN,
        actor_type: AuditActorType = AuditActorType.USER,
    ) -> ToolExpenseResponse:
        await ToolExpenseCategoryService(self.db).ensure_category(data.category)
        payload = data.model_dump()
        payload["source"] = source.value
        expense = await self.create(payload)
        await index_expense(self.db, expense)
        await AuditService(self.db).record_domain(
            action="expense.created",
            resource_type="expense",
            resource_id=expense.id,
            actor_type=actor_type,
            source=source,
            metadata={"tool_name": expense.tool_name},
        )
        return self._to_response(expense)

    async def update_expense(
        self,
        expense_id: int,
        data: ToolExpenseUpdate,
    ) -> ToolExpenseResponse:
        expense = await self.get(expense_id)
        payload = data.model_dump(exclude_unset=True)
        if "category" in payload:
            await ToolExpenseCategoryService(self.db).ensure_category(payload["category"])
        for key, value in payload.items():
            setattr(expense, key, value)
        await self.db.flush()
        await self.db.refresh(expense)
        await index_expense(self.db, expense)
        await AuditService(self.db).record_domain(
            action="expense.updated",
            resource_type="expense",
            resource_id=expense.id,
        )
        return self._to_response(expense)

    async def delete_expense(self, expense_id: int) -> None:
        await self.delete(expense_id)
        await remove_expense(self.db, expense_id)
        await AuditService(self.db).record_domain(
            action="expense.deleted",
            resource_type="expense",
            resource_id=expense_id,
        )

    async def list_expenses(
        self,
        date_from: date | None = None,
        date_to: date | None = None,
        tool_name: str | None = None,
        category: str | None = None,
    ) -> list[ToolExpenseResponse]:
        query = self._apply_filters(
            select(ToolExpense),
            date_from,
            date_to,
            tool_name,
            category,
        )
        query = query.order_by(
            ToolExpense.expense_date.desc(),
            ToolExpense.created_at.desc(),
        )
        result = await self.db.execute(query)
        return [self._to_response(e) for e in result.scalars().all()]

    async def get_expense(self, expense_id: int) -> ToolExpenseResponse:
        expense = await self.get(expense_id)
        return self._to_response(expense)

    async def export_csv(
        self,
        date_from: date | None = None,
        date_to: date | None = None,
        tool_name: str | None = None,
        category: str | None = None,
    ) -> str:
        expenses = await self.list_expenses(
            date_from=date_from,
            date_to=date_to,
            tool_name=tool_name,
            category=category,
        )
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(
            ["date", "category", "product", "amount", "currency", "notes", "source"],
        )
        for expense in expenses:
            writer.writerow(
                [
                    expense.expense_date.isoformat(),
                    _csv_cell(expense.category or ""),
                    _csv_cell(expense.tool_name),
                    expense.amount,
                    expense.currency,
                    _csv_cell(expense.notes or ""),
                    expense.source,
                ],
            )
        return buffer.getvalue()

    async def get_summary(
        self,
        date_from: date | None = None,
        date_to: date | None = None,
        display_currency: str = DEFAULT_EXPENSE_CURRENCY,
    ) -> ToolExpenseSummary:
        if display_currency not in ALLOWED_CURRENCIES:
            raise ValidationError(
                f"display_currency must be one of: {', '.join(ALLOWED_CURRENCIES)}"
            )

        query = self._apply_filters(select(ToolExpense), date_from, date_to)
        result = await self.db.execute(query)
        expenses = list(result.scalars().all())

        rates = await self._currency_svc.get_rates()
        rates_meta = await self._currency_svc.get_rates_meta()

        total = Decimal("0")
        month_totals: dict[str, Decimal] = defaultdict(Decimal)
        tool_totals: dict[str, Decimal] = defaultdict(Decimal)
        category_totals: dict[str, Decimal] = defaultdict(Decimal)

        for expense in expenses:
            amount = Decimal(str(expense.amount))
            converted = self._currency_svc.convert(
                amount,
                expense.currency,
                display_currency,
                rates,
            )
            total += converted
            period = expense.expense_date.strftime("%Y-%m")
            month_totals[period] += converted
            tool_totals[expense.tool_name] += converted
            category = expense.category or "Uncategorized"
            category_totals[category] += converted

        return ToolExpenseSummary(
            total=total.quantize(Decimal("0.01")),
            currency=display_currency,
            rates_updated_at=rates_meta.get("updated_at"),
            by_month=[
                ToolExpenseMonthTotal(period=period, total=amount)
                for period, amount in sorted(month_totals.items())
            ],
            by_tool=[
                ToolExpenseToolTotal(tool_name=name, total=amount)
                for name, amount in sorted(
                    tool_totals.items(), key=lambda item: item[1], reverse=True
                )
            ],
            by_category=[
                ToolExpenseCategoryTotal(category=name, total=amount)
                for name, amount in sorted(
                    category_totals.items(), key=lambda item: item[1], reverse=True
                )
            ],
        )
