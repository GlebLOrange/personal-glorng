from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.expense import ExchangeRatesResponse

CurrencyCode = Literal["USD", "EUR", "PLN", "BYN"]


class CurrencyConvertRequest(BaseModel):
    amount: Decimal = Field(gt=0, decimal_places=2)
    from_currency: CurrencyCode
    to_currency: CurrencyCode


class CurrencyConvertResponse(BaseModel):
    amount: Decimal
    from_currency: CurrencyCode
    to_currency: CurrencyCode
    converted: Decimal
    rates_updated_at: str | None = None


class CurrencyRatesResponse(ExchangeRatesResponse):
    pass
