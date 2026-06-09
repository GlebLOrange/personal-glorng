from pydantic import BaseModel, ConfigDict


class StripeDonationConfig(BaseModel):
    enabled: bool
    checkout_enabled: bool
    url: str | None = None


class TelegramDonationConfig(BaseModel):
    enabled: bool
    url: str | None = None


class CryptoDonationConfig(BaseModel):
    btc: str | None = None
    eth: str | None = None


class DonationsConfigResponse(BaseModel):
    stripe: StripeDonationConfig
    telegram: TelegramDonationConfig
    crypto: CryptoDonationConfig

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "stripe": {
                    "enabled": True,
                    "checkout_enabled": True,
                    "url": None,
                },
                "telegram": {"enabled": True, "url": "https://t.me/example"},
                "crypto": {"btc": "bc1...", "eth": "0x..."},
            }
        }
    )


class CheckoutSessionResponse(BaseModel):
    url: str

    model_config = ConfigDict(
        json_schema_extra={"example": {"url": "https://checkout.stripe.com/..."}}
    )


class WebhookAckResponse(BaseModel):
    status: str

    model_config = ConfigDict(json_schema_extra={"example": {"status": "ok"}})
