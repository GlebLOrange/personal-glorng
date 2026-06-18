import csv
import io
from calendar import monthrange
from collections import defaultdict
from datetime import date
from decimal import Decimal
from math import ceil

from app.core.catalogs import ALLOWED_CURRENCIES, DEFAULT_EXPENSE_CURRENCY
from app.core.exceptions import ValidationError
from app.core.utils import paginate_params
from app.db.documents.audit import AuditActorType, AuditSource
from app.db.documents.expense import Expense
from app.db.registry import DatabaseRegistry
from app.schemas.expense import (
    ExpenseCategoryTotal,
    ExpenseCreate,
    ExpenseListResponse,
    ExpenseMonthTotal,
    ExpenseResponse,
    ExpenseSummary,
    ExpenseToolTotal,
    ExpenseUpdate,
)
from app.services.audit import AuditService
from app.services.currency import CurrencyService
from app.services.expense_category import ExpenseCategoryService
from app.services.search_indexers.expense import index_expense, remove_expense

_CSV_FORMULA_PREFIXES = frozenset("=+-@\t\r")


def _csv_cell(value: str) -> str:
    """Prefix spreadsheet formula triggers to prevent CSV injection."""
    if value and value[0] in _CSV_FORMULA_PREFIXES:
        return f"'{value}"
    return value


class ExpenseService:
    def __init__(
        self,
        registry: DatabaseRegistry,
        *,
        currency_svc: CurrencyService | None = None,
    ) -> None:
        self.registry = registry
        self._currency_svc = currency_svc or CurrencyService()

    def _expenses(self):
        if self.registry.expenses is None:
            msg = "Expense repository is not initialized"
            raise RuntimeError(msg)
        return self.registry.expenses

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
    def _to_response(expense: Expense) -> ExpenseResponse:
        return ExpenseResponse.model_validate(expense)

    async def create_expense(
        self,
        data: ExpenseCreate,
        *,
        source: AuditSource = AuditSource.WEB_ADMIN,
        actor_type: AuditActorType = AuditActorType.USER,
    ) -> ExpenseResponse:
        await ExpenseCategoryService(self.registry).ensure_category(data.category)
        payload = data.model_dump()
        payload["source"] = source.value
        expense = Expense.model_validate(payload)
        expense = await self._expenses().expenses.insert(expense)
        await index_expense(self.registry, expense)
        await AuditService(self.registry).record_domain(
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
        data: ExpenseUpdate,
    ) -> ExpenseResponse:
        expense = await self._expenses().expenses.get(expense_id)
        payload = data.model_dump(exclude_unset=True)
        if "category" in payload:
            await ExpenseCategoryService(self.registry).ensure_category(
                payload["category"],
            )
        expense = await self._expenses().expenses.update_fields(expense_id, **payload)
        await index_expense(self.registry, expense)
        await AuditService(self.registry).record_domain(
            action="expense.updated",
            resource_type="expense",
            resource_id=expense.id,
        )
        return self._to_response(expense)

    async def delete_expense(self, expense_id: int) -> None:
        await self._expenses().expenses.delete(expense_id)
        await remove_expense(self.registry, expense_id)
        await AuditService(self.registry).record_domain(
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
        page: int = 1,
        per_page: int = 20,
        sort: str = "date_desc",
    ) -> ExpenseListResponse:
        offset, limit = paginate_params(page, per_page)
        expenses = await self._expenses().list_expenses(
            date_from=date_from,
            date_to=date_to,
            tool_name=tool_name,
            category=category,
            offset=offset,
            limit=limit,
            sort=sort,
        )
        total = await self._expenses().count_expenses(
            date_from=date_from,
            date_to=date_to,
            tool_name=tool_name,
            category=category,
        )
        return ExpenseListResponse(
            items=[self._to_response(e) for e in expenses],
            total=total,
            page=max(1, page),
            per_page=limit,
            pages=ceil(total / limit) if total > 0 else 0,
        )

    async def get_expense(self, expense_id: int) -> ExpenseResponse:
        expense = await self._expenses().expenses.get(expense_id)
        return self._to_response(expense)

    async def export_csv(
        self,
        date_from: date | None = None,
        date_to: date | None = None,
        tool_name: str | None = None,
        category: str | None = None,
    ) -> str:
        expenses = await self._expenses().list_expenses(
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
    ) -> ExpenseSummary:
        if display_currency not in ALLOWED_CURRENCIES:
            raise ValidationError(
                f"display_currency must be one of: {', '.join(ALLOWED_CURRENCIES)}"
            )

        expenses = await self._expenses().list_expenses(
            date_from=date_from,
            date_to=date_to,
        )

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

        return ExpenseSummary(
            total=total.quantize(Decimal("0.01")),
            currency=display_currency,
            rates_updated_at=rates_meta.get("updated_at"),
            by_month=[
                ExpenseMonthTotal(period=period, total=amount)
                for period, amount in sorted(month_totals.items())
            ],
            by_tool=[
                ExpenseToolTotal(tool_name=name, total=amount)
                for name, amount in sorted(
                    tool_totals.items(), key=lambda item: item[1], reverse=True
                )
            ],
            by_category=[
                ExpenseCategoryTotal(category=name, total=amount)
                for name, amount in sorted(
                    category_totals.items(), key=lambda item: item[1], reverse=True
                )
            ],
        )
