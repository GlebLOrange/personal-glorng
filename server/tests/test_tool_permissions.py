"""Capability denial matrix across admin tool APIs."""

import pytest
from httpx import AsyncClient

from app.core.security import create_access_token
from app.db.registry import DatabaseRegistry
from tests.factories import create_user

_DENIED_ENDPOINTS: list[tuple[str, str]] = [
    ("GET", "/api/tools/tasks"),
    ("GET", "/api/tools/expenses"),
    ("GET", "/api/feedback"),
    ("GET", "/api/tools/audit"),
    ("GET", "/api/tools/app-logs"),
    ("POST", "/api/tools/email/preview"),
]


@pytest.fixture
async def no_perms_client(
    client: AsyncClient,
    registry: DatabaseRegistry,
) -> AsyncClient:
    user = await create_user(
        registry,
        email="noperms@glorng.dev",
        permissions=[],
    )
    token = create_access_token(str(user.public_id), user_id=user.id)
    client.headers["Authorization"] = f"Bearer {token}"
    return client


@pytest.mark.asyncio
@pytest.mark.parametrize(("method", "path"), _DENIED_ENDPOINTS)
async def test_admin_tools_require_capabilities(
    no_perms_client: AsyncClient,
    method: str,
    path: str,
) -> None:
    if method == "GET":
        resp = await no_perms_client.get(path)
    else:
        resp = await no_perms_client.post(
            path,
            json={
                "to": "user@example.com",
                "subject": "Test",
                "body": "Body",
            },
        )
    assert resp.status_code == 403
