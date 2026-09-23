"""Unit tests for health checker probe helpers and uptime math."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.health_checker import (
    ProbeOutcome,
    compute_uptime_percent,
    probe_url,
)


def test_compute_uptime_percent_empty() -> None:
    assert compute_uptime_percent(0, 0) is None


def test_compute_uptime_percent_all_ok() -> None:
    assert compute_uptime_percent(10, 10) == 100.0


def test_compute_uptime_percent_partial() -> None:
    assert compute_uptime_percent(3, 4) == 75.0


@pytest.mark.asyncio
async def test_probe_url_rejects_private_host() -> None:
    outcome = await probe_url("http://127.0.0.1/")
    assert outcome.ok is False
    assert outcome.error is not None
    assert "not allowed" in outcome.error.lower()


@pytest.mark.asyncio
async def test_probe_url_success() -> None:
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.aclose = AsyncMock()

    mock_client = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with (
        patch(
            "app.services.health_checker.is_public_http_url",
            return_value=True,
        ),
        patch(
            "app.services.health_checker.get_public_http_url",
            new=AsyncMock(return_value=mock_response),
        ),
        patch(
            "app.services.health_checker.httpx.AsyncClient",
            return_value=mock_client,
        ),
        patch(
            "app.services.health_checker._resolve_dns",
            return_value=[],
        ),
        patch(
            "app.services.health_checker._ssl_expiry",
            return_value=None,
        ),
    ):
        outcome = await probe_url("https://example.com/")

    assert isinstance(outcome, ProbeOutcome)
    assert outcome.ok is True
    assert outcome.status_code == 200
    assert outcome.response_ms is not None
