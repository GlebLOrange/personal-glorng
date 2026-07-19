import pytest

from app.core.fernet_secrets import decrypt_secret, encrypt_secret
from app.services.github_credentials import (
    read_github_access_token,
    store_github_access_token,
)


def test_encrypt_decrypt_round_trip() -> None:
    secret = "test-jwt-secret-with-enough-entropy"
    plaintext = "gho_abcdefghijklmnopqrstuvwxyz1234567890"
    stored = encrypt_secret(plaintext, secret)
    assert stored.startswith("enc:")
    assert decrypt_secret(stored, secret) == plaintext


def test_decrypt_legacy_plaintext() -> None:
    secret = "test-jwt-secret-with-enough-entropy"
    legacy = "gho_legacy_plaintext_token"
    assert decrypt_secret(legacy, secret) == legacy


def test_decrypt_falls_back_to_legacy_secret() -> None:
    legacy_secret = "legacy-jwt-secret-with-enough-entropy"
    new_secret = "tokens-encryption-key-with-enough-entropy"
    plaintext = "gho_migrated_token"
    stored = encrypt_secret(plaintext, legacy_secret)
    assert (
        decrypt_secret(stored, new_secret, fallback_secrets=(legacy_secret,))
        == plaintext
    )


def test_github_credential_helpers(monkeypatch: pytest.MonkeyPatch) -> None:
    from app.settings import get_settings
    from tests.env_helpers import ENV_SCENARIOS_DIR, activate_env_file

    activate_env_file(monkeypatch, ENV_SCENARIOS_DIR / "fernet.env")

    token = "gho_test_token_value"
    stored = store_github_access_token(token)
    assert stored.startswith("enc:")
    assert read_github_access_token(stored) == token

    get_settings.cache_clear()


def test_github_credential_reads_jwt_secret_ciphertext(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Tokens encrypted with JWT_SECRET before key split still decrypt."""
    from app.settings import get_settings
    from tests.env_helpers import ENV_SCENARIOS_DIR, activate_env_file

    activate_env_file(monkeypatch, ENV_SCENARIOS_DIR / "fernet.env")
    settings = get_settings()
    # Ensure FERNET_SECRET is set so JWT fallback path is exercised.
    if not settings.FERNET_SECRET.strip():
        monkeypatch.setenv(
            "FERNET_SECRET",
            "dedicated-fernet-secret-with-enough-entropy",
        )
        get_settings.cache_clear()
        settings = get_settings()
    token = "gho_legacy_encrypted_token"
    stored = encrypt_secret(token, settings.JWT_SECRET)
    assert read_github_access_token(stored) == token
    get_settings.cache_clear()
