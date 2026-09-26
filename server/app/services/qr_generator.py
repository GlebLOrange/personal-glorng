"""QR code generation and persistence (Segno)."""

import segno
from segno import DataOverflowError

from app.core.exceptions import ApiError, NotFoundError
from app.core.pagination import build_paginated
from app.core.utils import DEFAULT_PER_PAGE, paginate_params
from app.db.documents.qr_code import QrCode, QrErrorLevel
from app.db.registry import DatabaseRegistry
from app.schemas.qr_generator import (
    QrCodeCreate,
    QrCodeListResponse,
    QrCodeResponse,
    content_preview,
)

SvgScale = 4


class QrGeneratorService:
    """Create, list, and render stored QR codes."""

    def __init__(self, registry: DatabaseRegistry) -> None:
        self.registry = registry

    def _repo(self):
        if self.registry.qr_codes is None:
            msg = "QR code repository is not initialized"
            raise RuntimeError(msg)
        return self.registry.qr_codes

    @staticmethod
    def svg_url(qr_id: int) -> str:
        return f"/api/tools/qr-generator/{qr_id}/svg"

    def _to_response(self, doc: QrCode) -> QrCodeResponse:
        return QrCodeResponse(
            id=doc.id,
            content_preview=content_preview(doc.content),
            label=doc.label,
            error_level=doc.error_level,
            svg_url=self.svg_url(doc.id),
            created_at=doc.created_at,
        )

    async def create(
        self,
        data: QrCodeCreate,
        *,
        created_by: int | None,
    ) -> QrCodeResponse:
        _validate_payload(data.content, data.error_level)
        doc = QrCode(
            content=data.content,
            label=data.label,
            error_level=data.error_level,
            created_by=created_by,
        )
        doc = await self._repo().insert(doc)
        return self._to_response(doc)

    async def get(self, qr_id: int) -> QrCode:
        row = await self._repo().get_or_none(qr_id)
        if row is None:
            raise NotFoundError(f"QR code with id {qr_id} not found")
        return row

    async def get_response(self, qr_id: int) -> QrCodeResponse:
        return self._to_response(await self.get(qr_id))

    async def list_recent(
        self,
        *,
        page: int = 1,
        per_page: int = DEFAULT_PER_PAGE,
    ) -> QrCodeListResponse:
        offset, limit = paginate_params(page, per_page)
        rows = await self._repo().list(
            offset=offset,
            limit=limit,
            sort=[("created_at", -1)],
        )
        total = await self._repo().count()
        items = [self._to_response(row) for row in rows]
        return build_paginated(items, total=total, page=page, per_page=per_page)

    async def render_svg(self, qr_id: int) -> str:
        doc = await self.get(qr_id)
        return render_qr_svg(doc.content, doc.error_level)


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
