import pytest

from app.core.fernet_secrets import decrypt_secret, encrypt_secret
from app.services.github_credentials import (
    read_github_access_token,
    read_google_refresh_token,
    store_github_access_token,
    store_google_refresh_token,
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


def test_github_credential_helpers(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("JWT_SECRET", "github-helper-test-jwt-secret-key-32chars")
    from app.settings import get_settings

    get_settings.cache_clear()

    token = "gho_test_token_value"
    stored = store_github_access_token(token)
    assert stored.startswith("enc:")
    assert read_github_access_token(stored) == token

    google_token = "1//0g_refresh_token_example"
    stored_google = store_google_refresh_token(google_token)
    assert stored_google.startswith("enc:")
    assert read_google_refresh_token(stored_google) == google_token

    get_settings.cache_clear()
