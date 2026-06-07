from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import Response

from app.core.deps import (
    AuthorizedUser,
    CurrencyServiceDep,
    ExpenseCategoryServiceDep,
    ExpenseServiceDep,
    require_capability,
)
from app.openapi import requires_capability
from app.schemas.common import MessageResponse
from app.schemas.currency import CurrencyConvertRequest, CurrencyConvertResponse
from app.schemas.date_filters import ExpenseDateFilter, expense_date_filter
from app.schemas.tool_expense import (
    ExchangeRatesResponse,
    ExpenseParseRequest,
    ExpenseParseResponse,
    ToolExpenseCreate,
    ToolExpenseResponse,
    ToolExpenseSummary,
    ToolExpenseUpdate,
)
from app.schemas.tool_expense_category import (
    ExpenseCategoryCreate,
    ExpenseCategoryResponse,
    ExpenseCategoryUpdate,
)
from app.todobot.utils.expense_nlp import parse_expense_text

router = APIRouter(
    prefix="/expenses",
    tags=["expenses"],
    dependencies=[Depends(require_capability("expenses", "read"))],
)


@router.get(
    "/categories",
    response_model=list[ExpenseCategoryResponse],
    summary="List expense categories",
    description=requires_capability("expenses", "read"),
)
async def list_categories(
    svc: ExpenseCategoryServiceDep,
    user: AuthorizedUser,  # noqa: ARG001
) -> list[ExpenseCategoryResponse]:
    return await svc.list_categories()


@router.post(
    "/categories",
    response_model=ExpenseCategoryResponse,
    summary="Create expense category",
    description=requires_capability("expenses", "write"),
    dependencies=[Depends(require_capability("expenses", "write"))],
)
async def create_category(
    data: ExpenseCategoryCreate,
    svc: ExpenseCategoryServiceDep,
    user: AuthorizedUser,  # noqa: ARG001
) -> ExpenseCategoryResponse:
    return await svc.create_category(data)


@router.put(
    "/categories/{category_id}",
    response_model=ExpenseCategoryResponse,
    summary="Update expense category",
    description=requires_capability("expenses", "write"),
    dependencies=[Depends(require_capability("expenses", "write"))],
)
async def update_category(
    category_id: int,
    data: ExpenseCategoryUpdate,
    svc: ExpenseCategoryServiceDep,
    user: AuthorizedUser,  # noqa: ARG001
) -> ExpenseCategoryResponse:
    return await svc.update_category(category_id, data)


@router.delete(
    "/categories/{category_id}",
    response_model=MessageResponse,
    summary="Delete expense category",
    description=requires_capability("expenses", "write"),
    dependencies=[Depends(require_capability("expenses", "write"))],
)
async def delete_category(
    category_id: int,
    svc: ExpenseCategoryServiceDep,
    user: AuthorizedUser,  # noqa: ARG001
) -> MessageResponse:
    await svc.delete_category(category_id)
    return MessageResponse(message="Category deleted")


@router.get(
    "/rates",
    response_model=ExchangeRatesResponse,
    summary="Get exchange rates",
    description=requires_capability("expenses", "read"),
)
async def get_exchange_rates(
    svc: CurrencyServiceDep,
    user: AuthorizedUser,  # noqa: ARG001
) -> ExchangeRatesResponse:
    meta = await svc.get_rates_meta()
    return ExchangeRatesResponse(**meta)


@router.post(
    "/convert",
    response_model=CurrencyConvertResponse,
    summary="Convert currency amount",
    description=requires_capability("expenses", "read"),
)
async def convert_currency(
    body: CurrencyConvertRequest,
    svc: CurrencyServiceDep,
    user: AuthorizedUser,  # noqa: ARG001
) -> CurrencyConvertResponse:
    rates = await svc.get_rates()
    meta = await svc.get_rates_meta()
    converted = svc.convert(
        body.amount,
        body.from_currency,
        body.to_currency,
        rates,
    )
    return CurrencyConvertResponse(
        amount=body.amount,
        from_currency=body.from_currency,
        to_currency=body.to_currency,
        converted=converted,
        rates_updated_at=meta.get("updated_at"),
    )


@router.get(
    "/summary",
    response_model=ToolExpenseSummary,
    description="Filter by month (YYYY-MM) or inclusive date range.",
)
async def get_summary(
    svc: ExpenseServiceDep,
    user: AuthorizedUser,  # noqa: ARG001
    filters: Annotated[ExpenseDateFilter, Depends(expense_date_filter)],
    display_currency: str = "USD",
) -> ToolExpenseSummary:
    resolved_from, resolved_to = filters.resolved_bounds()
    return await svc.get_summary(
        date_from=resolved_from,
        date_to=resolved_to,
        display_currency=display_currency,
    )


@router.post(
    "/parse",
    response_model=ExpenseParseResponse,
    summary="Parse expense from free text",
    description=requires_capability("expenses", "read"),
    dependencies=[Depends(require_capability("expenses", "read"))],
)
async def parse_expense(
    data: ExpenseParseRequest,
    user: AuthorizedUser,  # noqa: ARG001
) -> ExpenseParseResponse:
    parsed = parse_expense_text(
        data.text,
        default_currency=data.default_currency,
    )
    if not parsed.is_valid:
        return ExpenseParseResponse(valid=False, error=parsed.parse_error)
    return ExpenseParseResponse(
        valid=True,
        amount=parsed.amount,
        currency=parsed.currency,  # type: ignore[arg-type]
        category=parsed.category,
        tool_name=parsed.tool_name,
        expense_date=parsed.expense_date,
    )


@router.get(
    "",
    response_model=list[ToolExpenseResponse],
    description="Filter by month (YYYY-MM) or inclusive date range.",
)
async def list_expenses(
    svc: ExpenseServiceDep,
    user: AuthorizedUser,  # noqa: ARG001
    filters: Annotated[ExpenseDateFilter, Depends(expense_date_filter)],
    tool_name: str | None = None,
    category: str | None = None,
) -> list[ToolExpenseResponse]:
    resolved_from, resolved_to = filters.resolved_bounds()
    return await svc.list_expenses(
        date_from=resolved_from,
        date_to=resolved_to,
        tool_name=tool_name,
        category=category,
    )


@router.get(
    "/export",
    description="Filter by month (YYYY-MM) or inclusive date range.",
)
async def export_expenses(
    svc: ExpenseServiceDep,
    user: AuthorizedUser,  # noqa: ARG001
    filters: Annotated[ExpenseDateFilter, Depends(expense_date_filter)],
    tool_name: str | None = None,
    category: str | None = None,
) -> Response:
    resolved_from, resolved_to = filters.resolved_bounds()
    csv_content = await svc.export_csv(
        date_from=resolved_from,
        date_to=resolved_to,
        tool_name=tool_name,
        category=category,
    )
    return Response(
        content=csv_content,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="expenses.csv"'},
    )


@router.get(
    "/{expense_id}",
    response_model=ToolExpenseResponse,
    summary="Get expense by ID",
    description=requires_capability("expenses", "read"),
)
async def get_expense(
    expense_id: int,
    svc: ExpenseServiceDep,
    user: AuthorizedUser,  # noqa: ARG001
) -> ToolExpenseResponse:
    return await svc.get_expense(expense_id)


@router.post(
    "",
    response_model=ToolExpenseResponse,
    summary="Create expense",
    description=requires_capability("expenses", "write"),
    dependencies=[Depends(require_capability("expenses", "write"))],
)
async def create_expense(
    data: ToolExpenseCreate,
    svc: ExpenseServiceDep,
    user: AuthorizedUser,  # noqa: ARG001
) -> ToolExpenseResponse:
    return await svc.create_expense(data)


@router.put(
    "/{expense_id}",
    response_model=ToolExpenseResponse,
    summary="Update expense",
    description=requires_capability("expenses", "write"),
    dependencies=[Depends(require_capability("expenses", "write"))],
)
async def update_expense(
    expense_id: int,
    data: ToolExpenseUpdate,
    svc: ExpenseServiceDep,
    user: AuthorizedUser,  # noqa: ARG001
) -> ToolExpenseResponse:
    return await svc.update_expense(expense_id, data)


@router.delete(
    "/{expense_id}",
    response_model=MessageResponse,
    summary="Delete expense",
    description=requires_capability("expenses", "write"),
    dependencies=[Depends(require_capability("expenses", "write"))],
)
async def delete_expense(
    expense_id: int,
    svc: ExpenseServiceDep,
    user: AuthorizedUser,  # noqa: ARG001
) -> MessageResponse:
    await svc.delete_expense(expense_id)
    return MessageResponse(message="Expense deleted")
