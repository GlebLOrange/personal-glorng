"""Tests for resume PDF download endpoint."""

from __future__ import annotations

import pytest
from httpx import AsyncClient

from app.content.resume_data import RESUME_DATA
from app.core.utils import attachment_content_disposition


def _weasyprint_available() -> bool:
    try:
        from app.services.resume_pdf import render_resume_pdf

        return render_resume_pdf(dict(RESUME_DATA)).startswith(b"%PDF")
    except Exception:
        return False

WEASYPRINT_AVAILABLE = _weasyprint_available()

requires_weasyprint = pytest.mark.skipif(
    not WEASYPRINT_AVAILABLE,
    reason="WeasyPrint or system libraries (Pango/Cairo) unavailable",
)


@pytest.mark.asyncio
async def test_resume_pdf_download(
    client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """PDF endpoint returns a valid PDF attachment."""
    async def fake_get_cached_resume_pdf(_resume: dict[str, object]) -> bytes:
        """Return deterministic PDF bytes for the endpoint contract test."""
        return b"%PDF fake"

    monkeypatch.setattr(
        "app.routers.resume.get_cached_resume_pdf",
        fake_get_cached_resume_pdf,
    )

    resp = await client.get("/api/resume/pdf")
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/pdf"
    assert resp.headers["content-disposition"] == attachment_content_disposition(
        "gleb.y.cv.pdf",
    )
    assert resp.content.startswith(b"%PDF")


@pytest.mark.asyncio
async def test_cached_resume_pdf_renders_once(monkeypatch: pytest.MonkeyPatch) -> None:
    """Cached renderer reuses generated PDF bytes after the first render."""
    from app.services import resume_pdf

    calls = 0

    def fake_render_resume_pdf(_resume: dict[str, object]) -> bytes:
        """Return deterministic PDF bytes and track render calls."""
        nonlocal calls
        calls += 1
        return b"%PDF cached"

    resume_pdf.clear_resume_pdf_cache()
    monkeypatch.setattr(resume_pdf, "render_resume_pdf", fake_render_resume_pdf)
    try:
        first = await resume_pdf.get_cached_resume_pdf(dict(RESUME_DATA))
        second = await resume_pdf.get_cached_resume_pdf(dict(RESUME_DATA))
    finally:
        resume_pdf.clear_resume_pdf_cache()

    assert first == b"%PDF cached"
    assert second == first
    assert calls == 1


@requires_weasyprint
@pytest.mark.asyncio
async def test_render_resume_pdf_bytes() -> None:
    """Direct renderer produces PDF magic bytes."""
    from app.services.resume_pdf import render_resume_pdf

    pdf = render_resume_pdf(dict(RESUME_DATA))
    assert pdf.startswith(b"%PDF")
    assert len(pdf) > 500
