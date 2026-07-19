"""Google OAuth token persistence helpers."""

from app.core.fernet_secrets import decrypt_secret, encrypt_secret
from app.settings import get_settings


def store_google_refresh_token(plaintext: str) -> str:
    """Encrypt a Google OAuth refresh token before persisting."""
    return encrypt_secret(plaintext, get_settings().resolved_fernet_secret())


def read_google_refresh_token(stored: str) -> str:
    """Return a usable Google OAuth refresh token from stored value."""
    return decrypt_secret(stored, get_settings().resolved_fernet_secret())
