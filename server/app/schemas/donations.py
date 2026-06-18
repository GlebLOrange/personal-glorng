from pydantic import BaseModel, ConfigDict


class StripeDonationConfig(BaseModel):
    """Public Stripe donation availability."""

    enabled: bool
    checkout_enabled: bool
    url: str | None = None


class DonationLinkConfig(BaseModel):
    """Public external donation link availability."""

    enabled: bool
    url: str | None = None


class DonationsConfigResponse(BaseModel):
    """Public donation options for the portfolio support section."""

    stripe: StripeDonationConfig
    paypal: DonationLinkConfig
    patreon: DonationLinkConfig

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "stripe": {
                    "enabled": True,
                    "checkout_enabled": True,
                    "url": None,
                },
                "paypal": {"enabled": True, "url": "https://paypal.me/example"},
                "patreon": {"enabled": True, "url": "https://patreon.com/example"},
            }
        }
    )


class CheckoutSessionResponse(BaseModel):
    """Stripe Checkout session redirect URL."""

    url: str

    model_config = ConfigDict(
        json_schema_extra={"example": {"url": "https://checkout.stripe.com/..."}}
    )


class WebhookAckResponse(BaseModel):
    """Stripe webhook acknowledgement."""

    status: str

    model_config = ConfigDict(json_schema_extra={"example": {"status": "ok"}})
