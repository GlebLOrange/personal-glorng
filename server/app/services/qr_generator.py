"""QR code generation (Segno) — ephemeral, no Mongo persistence."""

import segno
from segno import DataOverflowError

from app.core.exceptions import ApiError
from app.schemas.qr_generator import (
    QrCodeCreate,
    QrCodeGenerateResponse,
    QrErrorLevel,
    content_preview,
)

SvgScale = 4


def generate_qr(data: QrCodeCreate) -> QrCodeGenerateResponse:
    """Validate payload, render SVG, return inline (A1/B1 — no DB write)."""
    _validate_payload(data.content, data.error_level)
    svg = render_qr_svg(data.content, data.error_level)
    return QrCodeGenerateResponse(
        content_preview=content_preview(data.content),
        label=data.label,
        error_level=data.error_level,
        svg=svg,
    )


def _validate_payload(content: str, error_level: QrErrorLevel) -> None:
    try:
        segno.make(content, error=error_level)
    except (ValueError, DataOverflowError) as exc:
        raise ApiError(
            422,
            "Content is too long for the selected error correction level",
        ) from exc


def render_qr_svg(content: str, error_level: QrErrorLevel) -> str:
    """Render a QR code as an SVG string."""
    try:
        qr = segno.make(content, error=error_level)
    except (ValueError, DataOverflowError) as exc:
        raise ApiError(422, "Invalid QR payload") from exc
    return qr.svg_inline(scale=SvgScale, border=2)
