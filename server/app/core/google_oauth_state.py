"""One-time Google Calendar OAuth state tokens stored in Redis."""

import secrets

from app.core.redis import cache_getdel, security_set
from app.core.redis_keys import OAUTH_GOOGLE_STATE_PREFIX

_STATE_TTL_SECONDS = 600


def google_oauth_state_key(state: str) -> str:
    """Return the Redis key for a pending Google OAuth state."""
    return f"{OAUTH_GOOGLE_STATE_PREFIX}{state}"


def generate_google_oauth_state() -> str:
    """Create a cryptographically random OAuth state value."""
    return secrets.token_urlsafe(32)


async def store_google_oauth_state(*, state: str, telegram_user_id: int) -> None:
    """Persist OAuth state until callback or TTL expiry."""
    await security_set(
        google_oauth_state_key(state),
        str(telegram_user_id),
        ttl=_STATE_TTL_SECONDS,
    )


async def consume_google_oauth_state(state: str) -> int | None:
    """Validate and delete a one-time OAuth state; return Telegram user id."""
    telegram_user_id_str = await cache_getdel(google_oauth_state_key(state))
    if not telegram_user_id_str:
        return None
    try:
        return int(telegram_user_id_str)
    except ValueError:
        return None
