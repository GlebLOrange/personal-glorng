"""Tests for captcha-gated multi-job maintenance admin endpoints."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient

from app.services.maintenance import reset_maintenance_state
from app.settings import get_settings
from tests.conftest import STRONG_PASSWORD
from tests.env_helpers import activate_env_file, scenario_env
from tests.factories import create_user

STATUS_URL = "/api/admin/maintenance"
RUN_URL = "/api/admin/maintenance/run"


@pytest.fixture(autouse=True)
def _reset_state() -> None:
    reset_maintenance_state()
    yield
    reset_maintenance_state()


@pytest.fixture
def maintenance_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    script = tmp_path / "db_maintenance.sh"
    script.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    script.chmod(0o755)
    env = scenario_env(
        tmp_path,
        TURNSTILE_SITE_KEY="site-key-test",
        TURNSTILE_SECRET_KEY="secret-key-test",
        DB_MAINTENANCE_ENABLED="true",
        DB_MAINTENANCE_SCRIPT=str(script),
    )
    activate_env_file(monkeypatch, env)
    yield script
    get_settings.cache_clear()


def _mock_turnstile_ok(client_cls: MagicMock) -> None:
    mock_client = AsyncMock()
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json.return_value = {"success": True}
    mock_client.post = AsyncMock(return_value=mock_resp)
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None
    client_cls.return_value = mock_client


@pytest.mark.asyncio
async def test_maintenance_requires_auth(client: AsyncClient) -> None:
    resp = await client.get(STATUS_URL)
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_maintenance_requires_superuser(client: AsyncClient, db: Any) -> None:
    user = await create_user(
        db,
        email="regular-maint@glorng.dev",
        password=STRONG_PASSWORD,
        permissions=[],
    )
    login = await client.post(
        "/api/auth/login",
        json={"email": user.email, "password": STRONG_PASSWORD},
    )
    token = login.cookies["access_token"]

    resp = await client.get(
        STATUS_URL,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_maintenance_status_defaults(auth_client: AsyncClient) -> None:
    resp = await auth_client.get(STATUS_URL)
    assert resp.status_code == 200
    data = resp.json()
    assert data["enabled"] is False
    assert data["host_jobs_ready"] is False
    assert data["status"] == "idle"
    assert data["site_key"] == ""
    assert data["job"] == ""
    assert data["report"] == ""


@pytest.mark.asyncio
async def test_run_rejects_bad_token(
    auth_client: AsyncClient,
    maintenance_env: Path,
) -> None:
    with patch("app.services.maintenance.httpx.AsyncClient") as client_cls:
        mock_client = AsyncMock()
        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json.return_value = {"success": False}
        mock_client.post = AsyncMock(return_value=mock_resp)
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        client_cls.return_value = mock_client

        with patch(
            "app.services.maintenance.asyncio.create_subprocess_exec",
            new_callable=AsyncMock,
        ) as spawn:
            resp = await auth_client.post(
                RUN_URL,
                json={"turnstile_token": "bad-token", "job": "backup"},
            )
            assert resp.status_code == 400
            spawn.assert_not_called()


@pytest.mark.asyncio
async def test_run_backup_disabled_never_spawns(
    auth_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    env = scenario_env(
        tmp_path,
        TURNSTILE_SITE_KEY="site-key-test",
        TURNSTILE_SECRET_KEY="secret-key-test",
        DB_MAINTENANCE_ENABLED="false",
        DB_MAINTENANCE_SCRIPT=str(tmp_path / "missing.sh"),
    )
    activate_env_file(monkeypatch, env)
    try:
        with patch("app.services.maintenance.httpx.AsyncClient") as client_cls:
            _mock_turnstile_ok(client_cls)

            with patch(
                "app.services.maintenance.asyncio.create_subprocess_exec",
                new_callable=AsyncMock,
            ) as spawn:
                resp = await auth_client.post(
                    RUN_URL,
                    json={"turnstile_token": "ok-token", "job": "backup"},
                )
                assert resp.status_code == 503
                spawn.assert_not_called()
    finally:
        get_settings.cache_clear()


@pytest.mark.asyncio
async def test_run_spawns_backup_script(
    auth_client: AsyncClient,
    maintenance_env: Path,
) -> None:
    proc = AsyncMock()
    proc.returncode = None
    proc.wait = AsyncMock(return_value=0)

    with (
        patch("app.services.maintenance.httpx.AsyncClient") as client_cls,
        patch(
            "app.services.maintenance.asyncio.create_subprocess_exec",
            new_callable=AsyncMock,
            return_value=proc,
        ) as spawn,
        patch(
            "app.services.maintenance.get_email_backend",
            return_value=AsyncMock(send=AsyncMock()),
        ),
    ):
        _mock_turnstile_ok(client_cls)
        resp = await auth_client.post(
            RUN_URL,
            json={"turnstile_token": "ok-token", "job": "backup"},
        )
        assert resp.status_code == 202
        body = resp.json()
        assert body["status"] == "running"
        assert body["job"] == "backup"
        spawn.assert_awaited_once()
        args, kwargs = spawn.await_args
        assert args == (str(maintenance_env),)
        assert "shell" not in kwargs


@pytest.mark.asyncio
async def test_run_stale_passes_flag(
    auth_client: AsyncClient,
    maintenance_env: Path,
) -> None:
    proc = AsyncMock()
    proc.returncode = None
    proc.wait = AsyncMock(return_value=0)

    with (
        patch("app.services.maintenance.httpx.AsyncClient") as client_cls,
        patch(
            "app.services.maintenance.asyncio.create_subprocess_exec",
            new_callable=AsyncMock,
            return_value=proc,
        ) as spawn,
        patch(
            "app.services.maintenance.get_email_backend",
            return_value=AsyncMock(send=AsyncMock()),
        ),
    ):
        _mock_turnstile_ok(client_cls)
        resp = await auth_client.post(
            RUN_URL,
            json={"turnstile_token": "ok-token", "job": "stale"},
        )
        assert resp.status_code == 202
        args, _kwargs = spawn.await_args
        assert args == (str(maintenance_env), "--check-stale")


@pytest.mark.asyncio
async def test_run_sync_inproc(
    auth_client: AsyncClient,
    maintenance_env: Path,
) -> None:
    with (
        patch("app.services.maintenance.httpx.AsyncClient") as client_cls,
        patch(
            "app.workers.tasks.process_sync_queue",
            new_callable=AsyncMock,
        ) as sync_mock,
        patch(
            "app.services.maintenance.get_email_backend",
        ) as backend_cls,
    ):
        _mock_turnstile_ok(client_cls)
        send = AsyncMock()
        backend_cls.return_value = MagicMock(send=send)

        resp = await auth_client.post(
            RUN_URL,
            json={"turnstile_token": "ok-token", "job": "sync"},
        )
        assert resp.status_code == 202
        assert resp.json()["job"] == "sync"

        for _ in range(50):
            if sync_mock.await_count:
                break
            await asyncio_sleep_brief()

        sync_mock.assert_awaited()
        send.assert_awaited()


@pytest.mark.asyncio
async def test_run_seed_blocked_in_production(
    auth_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    env = scenario_env(
        tmp_path,
        TURNSTILE_SITE_KEY="site-key-test",
        TURNSTILE_SECRET_KEY="secret-key-test",
        APP_ENV="production",
        MAINTENANCE_SEED_ENABLED="false",
        UNTRUSTED_URL_TOOLS_ENABLED="false",
    )
    activate_env_file(monkeypatch, env)
    try:
        with patch("app.services.maintenance.httpx.AsyncClient") as client_cls:
            _mock_turnstile_ok(client_cls)
            resp = await auth_client.post(
                RUN_URL,
                json={"turnstile_token": "ok-token", "job": "seed"},
            )
            assert resp.status_code == 403
    finally:
        get_settings.cache_clear()


async def asyncio_sleep_brief() -> None:
    """Yield so background maintenance tasks can progress in tests."""
    import asyncio

    await asyncio.sleep(0.01)
