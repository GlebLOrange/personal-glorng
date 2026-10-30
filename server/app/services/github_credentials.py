"""GitHub OAuth token persistence helpers."""

from app.core.fernet_secrets import read_secret_at_rest, store_secret_at_rest


def store_github_access_token(plaintext: str) -> str:
    """Encrypt a GitHub OAuth access token before persisting."""
    return store_secret_at_rest(plaintext)


def read_github_access_token(stored: str) -> str:
    """Return a usable GitHub OAuth access token from stored value."""
    return read_secret_at_rest(stored)
