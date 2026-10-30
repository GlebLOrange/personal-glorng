"""Google OAuth token persistence helpers."""

from app.core.fernet_secrets import read_secret_at_rest, store_secret_at_rest


def store_google_refresh_token(plaintext: str) -> str:
    """Encrypt a Google OAuth refresh token before persisting."""
    return store_secret_at_rest(plaintext)


def read_google_refresh_token(stored: str) -> str:
    """Return a usable Google OAuth refresh token from stored value."""
    return read_secret_at_rest(stored)
