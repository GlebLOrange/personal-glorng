"""Symmetric encryption for secrets stored at rest (Fernet + SHA-256 key derivation)."""

import base64
import hashlib

from cryptography.fernet import Fernet, InvalidToken

_ENCRYPTED_PREFIX = "enc:"


def _fernet_key(secret: str) -> bytes:
    digest = hashlib.sha256(secret.encode()).digest()
    return base64.urlsafe_b64encode(digest)


def encrypt_secret(plaintext: str, secret: str) -> str:
    """Encrypt a secret for database storage."""
    token = Fernet(_fernet_key(secret)).encrypt(plaintext.encode())
    return f"{_ENCRYPTED_PREFIX}{token.decode()}"


def decrypt_secret(
    stored: str,
    secret: str,
    *,
    fallback_secrets: tuple[str, ...] = (),
) -> str:
    """Decrypt a stored secret; return legacy plaintext values unchanged.

    Tries ``secret`` first, then each entry in ``fallback_secrets`` (e.g. legacy
    JWT_SECRET ciphertext after rotating to FERNET_SECRET).
    """
    if not stored.startswith(_ENCRYPTED_PREFIX):
        return stored
    payload = stored[len(_ENCRYPTED_PREFIX) :].encode()
    candidates = (secret, *fallback_secrets)
    last_error: InvalidToken | None = None
    for candidate in candidates:
        if not candidate:
            continue
        try:
            return Fernet(_fernet_key(candidate)).decrypt(payload).decode()
        except InvalidToken as exc:
            last_error = exc
    msg = "Failed to decrypt stored secret"
    raise ValueError(msg) from last_error
