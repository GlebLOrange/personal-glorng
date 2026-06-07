"""OAuth token persistence helpers (encrypt at rest via Fernet)."""

from app.core.fernet_secrets import decrypt_secret, encrypt_secret
from app.settings import get_settings


def _encryption_key() -> str:
    return get_settings().JWT_SECRET


def store_github_access_token(plaintext: str) -> str:
    """Encrypt a GitHub OAuth access token before persisting."""
    return encrypt_secret(plaintext, _encryption_key())


def read_github_access_token(stored: str) -> str:
    """Return a usable GitHub OAuth access token from stored value."""
    return decrypt_secret(stored, _encryption_key())


def store_google_refresh_token(plaintext: str) -> str:
    """Encrypt a Google OAuth refresh token before persisting."""
    return encrypt_secret(plaintext, _encryption_key())


def read_google_refresh_token(stored: str) -> str:
    """Return a usable Google OAuth refresh token from stored value."""
    return decrypt_secret(stored, _encryption_key())
