from typing import Any

from fastapi import APIRouter

from app.settings import get_settings

router = APIRouter()


@router.get(
    "/config",
    summary="Get donation config",
    description="Public donation links and crypto addresses.",
)
async def get_donations_config() -> dict[str, Any]:
    settings = get_settings()
    return {
        "stripe": {
            "enabled": bool(settings.STRIPE_LINK),
            "url": settings.STRIPE_LINK,
        },
        "telegram": {
            "enabled": bool(settings.TELEGRAM_LINK),
            "url": settings.TELEGRAM_LINK,
        },
        "crypto": {
            "btc": settings.CRYPTO_BTC_ADDRESS,
            "eth": settings.CRYPTO_ETH_ADDRESS,
        },
    }
