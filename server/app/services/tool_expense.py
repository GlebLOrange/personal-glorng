from calendar import monthrange
from collections import defaultdict
from datetime import date
from decimal import Decimal

from sqlalchemy import ColumnElement, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ValidationError
from app.db.models.audit_event import AuditActorType, AuditCategory, AuditSource
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
from app.services.audit import AuditRecord, AuditService
from app.services.base import CRUDService
from app.services.currency import ALLOWED_CURRENCIES, CurrencyService


class ToolExpenseService(CRUDService[ToolExpense]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, ToolExpense)

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
    def resolve_date_range(
        *,
        month: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> tuple[date | None, date | None]:
        if month:
            start, end = ToolExpenseService.month_date_bounds(month)
            return start, end
        return date_from, date_to

    def _month_period_expr(self) -> ColumnElement[str]:
        dialect = self.db.get_bind().dialect.name
        if dialect == "postgresql":
            return func.to_char(
                func.date_trunc("month", ToolExpense.expense_date),
                "YYYY-MM",
            )
        return func.strftime("%Y-%m", ToolExpense.expense_date)

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

    async def create_expense(self, data: ToolExpenseCreate) -> ToolExpenseResponse:
        expense = await self.create(data.model_dump())
        await AuditService(self.db).record(
            AuditRecord(
                category=AuditCategory.DOMAIN,
                action="expense.created",
                actor_type=AuditActorType.USER,
                source=AuditSource.WEB_ADMIN,
                resource_type="expense",
                resource_id=expense.id,
                metadata={"tool_name": expense.tool_name},
            ),
        )
        return self._to_response(expense)

    async def update_expense(
        self,
        expense_id: int,
        data: ToolExpenseUpdate,
    ) -> ToolExpenseResponse:
        expense = await self.get(expense_id)
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(expense, key, value)
        await self.db.flush()
        await self.db.refresh(expense)
        await AuditService(self.db).record(
            AuditRecord(
                category=AuditCategory.DOMAIN,
                action="expense.updated",
                actor_type=AuditActorType.USER,
                source=AuditSource.WEB_ADMIN,
                resource_type="expense",
                resource_id=expense.id,
            ),
        )
        return self._to_response(expense)

    async def delete_expense(self, expense_id: int) -> None:
        await self.delete(expense_id)
        await AuditService(self.db).record(
            AuditRecord(
                category=AuditCategory.DOMAIN,
                action="expense.deleted",
                actor_type=AuditActorType.USER,
                source=AuditSource.WEB_ADMIN,
                resource_type="expense",
                resource_id=expense_id,
            ),
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

    async def get_all_categories(self) -> list[str]:
        result = await self.db.execute(
            select(ToolExpense.category)
            .where(ToolExpense.category.is_not(None))
            .distinct()
            .order_by(ToolExpense.category)
        )
        return [row[0] for row in result if row[0]]

    async def get_summary(
        self,
        date_from: date | None = None,
        date_to: date | None = None,
        display_currency: str = "USD",
    ) -> ToolExpenseSummary:
        if display_currency not in ALLOWED_CURRENCIES:
            raise ValidationError(
                f"display_currency must be one of: {', '.join(ALLOWED_CURRENCIES)}"
            )

        query = self._apply_filters(select(ToolExpense), date_from, date_to)
        result = await self.db.execute(query)
        expenses = list(result.scalars().all())

        currency_svc = CurrencyService()
        rates = await currency_svc.get_rates()
        rates_meta = await currency_svc.get_rates_meta()

        total = Decimal("0")
        month_totals: dict[str, Decimal] = defaultdict(Decimal)
        tool_totals: dict[str, Decimal] = defaultdict(Decimal)
        category_totals: dict[str, Decimal] = defaultdict(Decimal)

        for expense in expenses:
            amount = Decimal(str(expense.amount))
            converted = currency_svc.convert(
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
