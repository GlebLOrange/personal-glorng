import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_email_preview_escapes_html(auth_client: AsyncClient) -> None:
    resp = await auth_client.post(
        "/api/tools/email/preview",
        json={
            "to": "user@example.com",
            "subject": "Test",
            "body": "<script>alert(1)</script>",
        },
    )
    assert resp.status_code == 200
    html = resp.json()["html"]
    assert "<script>" not in html
    assert "alert(1)" in html


@pytest.mark.asyncio
async def test_email_preview_unauthorized(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/tools/email/preview",
        json={"to": "user@example.com", "subject": "Hi", "body": "Hello"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_email_subject_rejects_crlf(auth_client: AsyncClient) -> None:
    resp = await auth_client.post(
        "/api/tools/email/preview",
        json={
            "to": "user@example.com",
            "subject": "Hi\r\nBcc: evil@example.com",
            "body": "Hello",
        },
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_email_body_max_length(auth_client: AsyncClient) -> None:
    resp = await auth_client.post(
        "/api/tools/email/preview",
        json={
            "to": "user@example.com",
            "subject": "Hi",
            "body": "x" * 5001,
        },
    )
    assert resp.status_code == 422
