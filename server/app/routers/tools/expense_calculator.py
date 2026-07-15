"""Public expense calculator (currency) and superuser state persistence."""

from fastapi import APIRouter, Depends

from app.core.deps import AdminUser, CurrencyServiceDep
from app.core.rate_limit import rate_limit_api
from app.db.deps import DbRegistry
from app.schemas.currency import CurrencyConvertRequest, CurrencyConvertResponse
from app.schemas.expense import ExchangeRatesResponse
from app.schemas.expense_calculator import ExpenseCalculatorState
from app.services.expense_calculator import get_calculator_state, save_calculator_state

router = APIRouter(
    prefix="/expense-calculator",
    tags=["expense-calculator"],
)


@router.get(
    "/rates",
    response_model=ExchangeRatesResponse,
    summary="Get exchange rates",
    description="Public exchange rates for the expense calculator (rate limited).",
    dependencies=[Depends(rate_limit_api)],
)
async def get_exchange_rates(svc: CurrencyServiceDep) -> ExchangeRatesResponse:
    meta = await svc.get_rates_meta()
    return ExchangeRatesResponse(**meta)


@router.post(
    "/convert",
    response_model=CurrencyConvertResponse,
    summary="Convert currency amount",
    description="Public currency conversion for the expense calculator (rate limited).",
    dependencies=[Depends(rate_limit_api)],
)
async def convert_currency(
    body: CurrencyConvertRequest,
    svc: CurrencyServiceDep,
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
    "/state",
    response_model=ExpenseCalculatorState,
    summary="Get saved calculator state",
    description="Superuser-only persisted calculator snapshot.",
)
async def get_state(user: AdminUser) -> ExpenseCalculatorState:
    state = get_calculator_state(user)
    if state is None:
        return ExpenseCalculatorState()
    return state


@router.put(
    "/state",
    response_model=ExpenseCalculatorState,
    summary="Save calculator state",
    description="Superuser-only persisted calculator snapshot.",
)
async def put_state(
    body: ExpenseCalculatorState,
    registry: DbRegistry,
    user: AdminUser,
) -> ExpenseCalculatorState:
    return await save_calculator_state(registry, user, body)
