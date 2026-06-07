import pytest
from httpx import AsyncClient

from app.core.email import (
    ConsoleBackend,
    render_verification_email,
    render_verification_email_plain,
)


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
async def test_console_backend_logs_metadata_only(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    logged: list[dict[str, object]] = []

    def capture_info(
        _message: str, *, context: dict[str, object] | None = None
    ) -> None:
        logged.append(context or {})

    monkeypatch.setattr("app.core.email.logger.info", capture_info)

    token = "super-secret-token"
    html = render_verification_email(token, "https://example.com")
    plain = render_verification_email_plain(token, "https://example.com")
    await ConsoleBackend().send("user@example.com", "Verify your email", html, plain)

    assert len(logged) == 1
    context = logged[0]
    assert context["to"] == "user@example.com"
    assert context["subject"] == "Verify your email"
    assert "html_bytes" in context
    assert "plain_bytes" in context
    assert "body_preview" not in context
    assert "plain_preview" not in context
    assert token not in str(context)


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
