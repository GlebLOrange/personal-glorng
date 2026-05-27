from datetime import date

from fastapi import APIRouter

from app.core.deps import AdminUser, DbSession
from app.core.logging import logger
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

router = APIRouter(prefix="/expenses")


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
    date_from: date | None = None,
    date_to: date | None = None,
    display_currency: str = "USD",
) -> ToolExpenseSummary:
    svc = ToolExpenseService(db)
    return await svc.get_summary(
        date_from=date_from,
        date_to=date_to,
        display_currency=display_currency,
    )


@router.get("", response_model=list[ToolExpenseResponse])
async def list_expenses(
    db: DbSession,
    user: AdminUser,  # noqa: ARG001
    date_from: date | None = None,
    date_to: date | None = None,
    tool_name: str | None = None,
    category: str | None = None,
) -> list[ToolExpenseResponse]:
    svc = ToolExpenseService(db)
    return await svc.list_expenses(
        date_from=date_from,
        date_to=date_to,
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
    user: AdminUser,
) -> ToolExpenseResponse:
    svc = ToolExpenseService(db)
    expense = await svc.create_expense(data)
    logger.info(
        "Tool expense created",
        context={"expense_id": expense.id, "user_id": user.id},
    )
    return expense


@router.put("/{expense_id}", response_model=ToolExpenseResponse)
async def update_expense(
    expense_id: int,
    data: ToolExpenseUpdate,
    db: DbSession,
    user: AdminUser,
) -> ToolExpenseResponse:
    svc = ToolExpenseService(db)
    expense = await svc.update_expense(expense_id, data)
    logger.info(
        "Tool expense updated",
        context={"expense_id": expense_id, "user_id": user.id},
    )
    return expense


@router.delete("/{expense_id}", response_model=MessageResponse)
async def delete_expense(
    expense_id: int,
    db: DbSession,
    user: AdminUser,
) -> MessageResponse:
    svc = ToolExpenseService(db)
    await svc.delete(expense_id)
    logger.info(
        "Tool expense deleted",
        context={"expense_id": expense_id, "user_id": user.id},
    )
    return MessageResponse(message="Expense deleted")
