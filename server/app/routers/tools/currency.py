from fastapi import APIRouter, Depends

from app.core.deps import AdminUser, require_admin
from app.schemas.currency import (
    CurrencyConvertRequest,
    CurrencyConvertResponse,
    CurrencyRatesResponse,
)
from app.services.currency import CurrencyService

router = APIRouter(prefix="/currency", dependencies=[Depends(require_admin)])


@router.get("/rates", response_model=CurrencyRatesResponse)
async def get_rates(
    user: AdminUser,  # noqa: ARG001
) -> CurrencyRatesResponse:
    meta = await CurrencyService().get_rates_meta()
    return CurrencyRatesResponse(**meta)


@router.post("/convert", response_model=CurrencyConvertResponse)
async def convert_currency(
    body: CurrencyConvertRequest,
    user: AdminUser,  # noqa: ARG001
) -> CurrencyConvertResponse:
    svc = CurrencyService()
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
