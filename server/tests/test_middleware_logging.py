"""Middleware request logging correlated with app log persistence."""

from pathlib import Path

import pytest
from httpx import AsyncClient

from app.core.app_log_persist import _drain_queue
from app.core.middleware import (
    _read_body_for_log,
    _sanitize_body_for_log,
    _should_skip_body_log,
)
from app.settings import get_settings
from tests.env_helpers import activate_env_file, scenario_env


@pytest.mark.asyncio
@pytest.mark.e2e_api
async def test_request_completed_log_includes_request_id(
    client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    activate_env_file(
        monkeypatch, scenario_env(tmp_path, APP_LOG_PERSIST_MIN_LEVEL="INFO")
    )

    _drain_queue()
    resp = await client.get("/api/resume")
    assert resp.status_code == 200

    entries = _drain_queue()
    assert any(
        entry.get("message") == "Request completed" and entry.get("request_id")
        for entry in entries
    )
    get_settings.cache_clear()


def test_body_log_redacts_nested_list_secrets() -> None:
    body = b'[{"token": "abc"}, {"nested": {"password": "secret"}}]'

    sanitized = _sanitize_body_for_log(body, content_type="application/json")

    assert sanitized == (
        '[{"token": "[REDACTED]"}, {"nested": {"password": "[REDACTED]"}}]'
    )


def test_body_log_omits_raw_non_json_body() -> None:
    body = b"password=secret&token=abc"

    sanitized = _sanitize_body_for_log(
        body,
        content_type="application/x-www-form-urlencoded",
    )

    assert sanitized == (
        "[non-json request body omitted: 25 bytes, "
        "content_type=application/x-www-form-urlencoded]"
    )
    assert "secret" not in sanitized
    assert "token=abc" not in sanitized


def test_body_log_skips_multipart_and_binary_content_types() -> None:
    assert _should_skip_body_log("multipart/form-data; boundary=abc") is True
    assert _should_skip_body_log("application/octet-stream") is True
    assert _should_skip_body_log("application/json") is False


@pytest.mark.asyncio
async def test_read_body_for_log_skips_oversized_content_length() -> None:
    class _Req:
        def __init__(self) -> None:
            self.headers = {
                "content-type": "application/json",
                "content-length": "999999",
            }

        async def body(self) -> bytes:
            raise AssertionError("body should not be read when Content-Length is large")

    assert await _read_body_for_log(_Req()) is None  # type: ignore[arg-type]
