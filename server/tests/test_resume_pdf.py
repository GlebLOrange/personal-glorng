"""Tests for resume PDF download endpoint."""

from __future__ import annotations

import pytest
from httpx import AsyncClient

from app.content.resume_data import RESUME_DATA


def _weasyprint_available() -> bool:
    try:
        from app.services.resume_pdf import render_resume_pdf

        return render_resume_pdf(dict(RESUME_DATA)).startswith(b"%PDF")
    except Exception:
        return False


WEASYPRINT_AVAILABLE = _weasyprint_available()

pytestmark = pytest.mark.skipif(
    not WEASYPRINT_AVAILABLE,
    reason="WeasyPrint or system libraries (Pango/Cairo) unavailable",
)


@pytest.mark.asyncio
async def test_resume_pdf_download(client: AsyncClient) -> None:
    """PDF endpoint returns a valid PDF attachment."""
    resp = await client.get("/api/resume/pdf")
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/pdf"
    assert "attachment" in resp.headers.get("content-disposition", "").lower()
    assert resp.content.startswith(b"%PDF")


@pytest.mark.asyncio
async def test_render_resume_pdf_bytes() -> None:
    """Direct renderer produces PDF magic bytes."""
    from app.services.resume_pdf import render_resume_pdf

    pdf = render_resume_pdf(dict(RESUME_DATA))
    assert pdf.startswith(b"%PDF")
    assert len(pdf) > 500
