"""GitHub OAuth token persistence helpers."""

from app.core.fernet_secrets import decrypt_secret, encrypt_secret
from app.settings import get_settings


def store_github_access_token(plaintext: str) -> str:
    """Encrypt a GitHub OAuth access token before persisting."""
    return encrypt_secret(plaintext, get_settings().resolved_fernet_secret())


def read_github_access_token(stored: str) -> str:
    """Return a usable GitHub OAuth access token from stored value."""
    settings = get_settings()
    primary = settings.resolved_fernet_secret()
    fallback = ()
    if settings.FERNET_SECRET.strip() and primary != settings.JWT_SECRET:
        fallback = (settings.JWT_SECRET,)
    return decrypt_secret(stored, primary, fallback_secrets=fallback)
