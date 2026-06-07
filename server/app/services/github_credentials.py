"""GitHub OAuth token persistence helpers."""

from app.core.fernet_secrets import decrypt_secret, encrypt_secret
from app.settings import get_settings


def store_github_access_token(plaintext: str) -> str:
    """Encrypt a GitHub OAuth access token before persisting."""
    return encrypt_secret(plaintext, get_settings().JWT_SECRET)


def read_github_access_token(stored: str) -> str:
    """Return a usable GitHub OAuth access token from stored value."""
    return decrypt_secret(stored, get_settings().JWT_SECRET)
