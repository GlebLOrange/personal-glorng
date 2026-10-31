"""Unit tests for todobot Telegram ping helper."""

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.exceptions import ServiceUnavailableError, ValidationError
from app.core.telegram import ping_todobot

if TYPE_CHECKING:
    from _pytest.monkeypatch import MonkeyPatch


@pytest.mark.asyncio
async def test_ping_todobot_requires_token(monkeypatch: MonkeyPatch) -> None:
    """Missing todobot token raises ValidationError before calling Telegram."""
    settings = MagicMock()
    settings.TELEGRAM_BOT_TO_DO_TOKEN = ""
    settings.TELEGRAM_ALLOWED_USER_ID = 123
    monkeypatch.setattr("app.core.telegram.get_settings", lambda: settings)

    with pytest.raises(ValidationError, match="TELEGRAM_BOT_TO_DO_TOKEN"):
        await ping_todobot()


@pytest.mark.asyncio
async def test_ping_todobot_requires_allowed_user(monkeypatch: MonkeyPatch) -> None:
    """Missing allowlisted user id raises ValidationError."""
    settings = MagicMock()
    settings.TELEGRAM_BOT_TO_DO_TOKEN = "token"
    settings.TELEGRAM_ALLOWED_USER_ID = 0
    monkeypatch.setattr("app.core.telegram.get_settings", lambda: settings)

    with pytest.raises(ValidationError, match="TELEGRAM_ALLOWED_USER_ID"):
        await ping_todobot()


@pytest.mark.asyncio
async def test_ping_todobot_success(monkeypatch: MonkeyPatch) -> None:
    """getMe + sendMessage success returns structured result."""
    settings = MagicMock()
    settings.TELEGRAM_BOT_TO_DO_TOKEN = "token"
    settings.TELEGRAM_ALLOWED_USER_ID = 99
    monkeypatch.setattr("app.core.telegram.get_settings", lambda: settings)

    me_resp = MagicMock()
    me_resp.raise_for_status = MagicMock()
    me_resp.json.return_value = {
        "ok": True,
        "result": {"id": 7, "username": "todo_bot"},
    }
    send_resp = MagicMock()
    send_resp.raise_for_status = MagicMock()
    send_resp.json.return_value = {"ok": True, "result": {}}

    client = AsyncMock()
    client.get = AsyncMock(return_value=me_resp)
    client.post = AsyncMock(return_value=send_resp)
    client.__aenter__ = AsyncMock(return_value=client)
    client.__aexit__ = AsyncMock(return_value=None)

    with patch("app.core.telegram.httpx.AsyncClient", return_value=client):
        result = await ping_todobot()

    assert result.ok is True
    assert result.bot_username == "todo_bot"
    assert result.bot_id == 7
    assert result.message_sent is True
    assert "@todo_bot" in result.detail
    client.get.assert_awaited_once()
    client.post.assert_awaited_once()


@pytest.mark.asyncio
async def test_ping_todobot_telegram_error(monkeypatch: MonkeyPatch) -> None:
    """Transport failures become ServiceUnavailableError."""
    settings = MagicMock()
    settings.TELEGRAM_BOT_TO_DO_TOKEN = "token"
    settings.TELEGRAM_ALLOWED_USER_ID = 99
    monkeypatch.setattr("app.core.telegram.get_settings", lambda: settings)

    client = AsyncMock()
    client.get = AsyncMock(side_effect=RuntimeError("network down"))
    client.__aenter__ = AsyncMock(return_value=client)
    client.__aexit__ = AsyncMock(return_value=None)

    with (
        patch("app.core.telegram.httpx.AsyncClient", return_value=client),
        pytest.raises(ServiceUnavailableError, match="todobot ping failed"),
    ):
        await ping_todobot()
