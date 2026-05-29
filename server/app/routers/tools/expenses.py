from datetime import date

from fastapi import APIRouter, Depends

from app.core.deps import AdminUser, DbSession, require_admin
from app.schemas.common import MessageResponse
from app.schemas.tool_expense import (
    ExchangeRatesResponse,
    ToolExpenseCreate,
    ToolExpenseResponse,
    ToolExpenseSummary,
    ToolExpenseUpdate,
)
from app.services.currency import CurrencyService
from app.services.tool_expense import ToolExpenseService

router = APIRouter(prefix="/expenses", dependencies=[Depends(require_admin)])


@router.get("/categories", response_model=list[str])
async def list_categories(
    db: DbSession,
    user: AdminUser,  # noqa: ARG001
) -> list[str]:
    svc = ToolExpenseService(db)
    return await svc.get_all_categories()


@router.get("/rates", response_model=ExchangeRatesResponse)
async def get_exchange_rates(
    user: AdminUser,  # noqa: ARG001
) -> ExchangeRatesResponse:
    meta = await CurrencyService().get_rates_meta()
    return ExchangeRatesResponse(**meta)


@router.get("/summary", response_model=ToolExpenseSummary)
async def get_summary(
    db: DbSession,
    user: AdminUser,  # noqa: ARG001
    month: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    display_currency: str = "USD",
) -> ToolExpenseSummary:
    svc = ToolExpenseService(db)
    resolved_from, resolved_to = svc.resolve_date_range(
        month=month,
        date_from=date_from,
        date_to=date_to,
    )
    return await svc.get_summary(
        date_from=resolved_from,
        date_to=resolved_to,
        display_currency=display_currency,
    )


@router.get("", response_model=list[ToolExpenseResponse])
async def list_expenses(
    db: DbSession,
    user: AdminUser,  # noqa: ARG001
    month: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    tool_name: str | None = None,
    category: str | None = None,
) -> list[ToolExpenseResponse]:
    svc = ToolExpenseService(db)
    resolved_from, resolved_to = svc.resolve_date_range(
        month=month,
        date_from=date_from,
        date_to=date_to,
    )
    return await svc.list_expenses(
        date_from=resolved_from,
        date_to=resolved_to,
        tool_name=tool_name,
        category=category,
    )


@router.get("/{expense_id}", response_model=ToolExpenseResponse)
async def get_expense(
    expense_id: int,
    db: DbSession,
    user: AdminUser,  # noqa: ARG001
) -> ToolExpenseResponse:
    svc = ToolExpenseService(db)
    return await svc.get_expense(expense_id)


@router.post("", response_model=ToolExpenseResponse)
async def create_expense(
    data: ToolExpenseCreate,
    db: DbSession,
    user: AdminUser,  # noqa: ARG001
) -> ToolExpenseResponse:
    svc = ToolExpenseService(db)
    return await svc.create_expense(data)


@router.put("/{expense_id}", response_model=ToolExpenseResponse)
async def update_expense(
    expense_id: int,
    data: ToolExpenseUpdate,
    db: DbSession,
    user: AdminUser,  # noqa: ARG001
) -> ToolExpenseResponse:
    svc = ToolExpenseService(db)
    return await svc.update_expense(expense_id, data)


@router.delete("/{expense_id}", response_model=MessageResponse)
async def delete_expense(
    expense_id: int,
    db: DbSession,
    user: AdminUser,  # noqa: ARG001
) -> MessageResponse:
    svc = ToolExpenseService(db)
    await svc.delete_expense(expense_id)
    return MessageResponse(message="Expense deleted")
