import json
import time
from decimal import Decimal
from typing import Literal

import httpx

from app.core.exceptions import ApiError
from app.core.logging import logger
from app.core.redis import cache_get, cache_set

CurrencyCode = Literal["USD", "EUR", "PLN", "BYN"]

ALLOWED_CURRENCIES: tuple[CurrencyCode, ...] = ("USD", "EUR", "PLN", "BYN")
RATES_CACHE_KEY = "currency:rates:USD"
RATES_API_URL = "https://open.er-api.com/v6/latest/USD"


class CurrencyService:
    """Fetch FX rates from Exchange Rate API open access (no API key)."""

    async def get_rates(self) -> dict[str, Decimal]:
        cached = await cache_get(RATES_CACHE_KEY)
        if cached:
            return self._parse_rates(json.loads(cached))

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(RATES_API_URL, timeout=10)
        except httpx.HTTPError as e:
            logger.error("Currency API unreachable", error=e)
            raise ApiError(502, "Currency exchange API is unreachable") from e

        if resp.status_code != 200:
            raise ApiError(502, f"Currency API returned {resp.status_code}")

        payload = resp.json()
        if payload.get("result") != "success":
            raise ApiError(502, "Currency API returned an error")

        ttl = self._cache_ttl(payload)
        await cache_set(RATES_CACHE_KEY, json.dumps(payload), ttl=ttl)
        return self._parse_rates(payload)

    @staticmethod
    def _cache_ttl(payload: dict) -> int:
        next_update = payload.get("time_next_update_unix")
        if isinstance(next_update, int):
            remaining = next_update - int(time.time())
            if remaining > 60:
                return remaining
        return 3600

    def _parse_rates(self, payload: dict) -> dict[str, Decimal]:
        raw = payload.get("rates", {})
        rates: dict[str, Decimal] = {}
        for code in ALLOWED_CURRENCIES:
            if code not in raw:
                raise ApiError(502, f"Currency API missing rate for {code}")
            rates[code] = Decimal(str(raw[code]))
        return rates

    async def get_rates_meta(self) -> dict:
        cached = await cache_get(RATES_CACHE_KEY)
        if cached:
            payload = json.loads(cached)
        else:
            await self.get_rates()
            cached = await cache_get(RATES_CACHE_KEY)
            payload = json.loads(cached) if cached else {}

        rates = self._parse_rates(payload) if payload else await self.get_rates()
        return {
            "base": "USD",
            "rates": {code: str(rates[code]) for code in ALLOWED_CURRENCIES},
            "updated_at": payload.get("time_last_update_utc"),
            "provider": "https://www.exchangerate-api.com",
        }

    @staticmethod
    def convert(
        amount: Decimal,
        from_currency: str,
        to_currency: str,
        rates: dict[str, Decimal],
    ) -> Decimal:
        if from_currency not in rates or to_currency not in rates:
            msg = "Unsupported currency for conversion"
            raise ValueError(msg)
        if from_currency == to_currency:
            return amount
        usd = amount / rates[from_currency]
        return (usd * rates[to_currency]).quantize(Decimal("0.01"))
