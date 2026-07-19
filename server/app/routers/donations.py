from fastapi import APIRouter, Depends, Request

from app.core.exceptions import ApiError
from app.core.rate_limit import RateLimiter
from app.core.uploads import read_request_body_bounded
from app.schemas.donations import (
    CheckoutSessionResponse,
    DonationLinkConfig,
    DonationsConfigResponse,
    StripeDonationConfig,
    WebhookAckResponse,
)
from app.services.stripe_donations import (
    create_checkout_session,
    handle_stripe_event,
    parse_stripe_event,
    verify_stripe_signature,
)
from app.settings import get_settings

router = APIRouter()

STRIPE_WEBHOOK_MAX_BODY_BYTES = 1024 * 1024

rate_limit_checkout = RateLimiter(requests=10, window=3600, fail_open=False)
rate_limit_stripe_webhook = RateLimiter(requests=30, window=60, fail_open=False)


@router.get(
    "/config",
    response_model=DonationsConfigResponse,
    summary="Get donation config",
    description="Public donation links for Stripe, PayPal, and Patreon.",
)
async def get_donations_config() -> DonationsConfigResponse:
    settings = get_settings()
    checkout_enabled = settings.stripe_checkout_enabled()
    legacy_link = settings.STRIPE_LINK
    return DonationsConfigResponse(
        stripe=StripeDonationConfig(
            enabled=checkout_enabled or bool(legacy_link),
            checkout_enabled=checkout_enabled,
            url=legacy_link,
        ),
        paypal=DonationLinkConfig(
            enabled=bool(settings.PAYPAL_DONATION_LINK),
            url=settings.PAYPAL_DONATION_LINK,
        ),
        patreon=DonationLinkConfig(
            enabled=bool(settings.PATREON_LINK),
            url=settings.PATREON_LINK,
        ),
    )


@router.post(
    "/checkout",
    response_model=CheckoutSessionResponse,
    summary="Create Stripe Checkout session",
    description="Returns a hosted Checkout URL when STRIPE_SECRET_KEY is configured.",
    dependencies=[Depends(rate_limit_checkout)],
)
async def create_donation_checkout() -> CheckoutSessionResponse:
    payload = await create_checkout_session()
    return CheckoutSessionResponse(url=payload["url"])


@router.post(
    "/webhook",
    response_model=WebhookAckResponse,
    summary="Stripe webhook",
    description="Receives signed Stripe events (checkout.session.completed).",
    dependencies=[Depends(rate_limit_stripe_webhook)],
)
async def stripe_webhook(request: Request) -> WebhookAckResponse:
    settings = get_settings()
    if not settings.stripe_webhook_enabled():
        raise ApiError(503, "Stripe webhooks are not configured")

    payload = await read_request_body_bounded(request, STRIPE_WEBHOOK_MAX_BODY_BYTES)
    verify_stripe_signature(
        payload=payload,
        signature_header=request.headers.get("stripe-signature"),
        secret=settings.STRIPE_WEBHOOK_SECRET,
    )
    event = parse_stripe_event(payload)
    result = await handle_stripe_event(event)
    return WebhookAckResponse(status=result.get("status", "ok"))
