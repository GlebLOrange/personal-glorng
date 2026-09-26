"""QR code generation (Segno) — public ephemeral + admin library."""

import segno
from segno import DataOverflowError

from app.core.exceptions import ApiError, NotFoundError
from app.core.pagination import build_paginated
from app.core.utils import DEFAULT_PER_PAGE, paginate_params
from app.db.documents.qr_code import QrCode, QrErrorLevel
from app.db.registry import DatabaseRegistry
from app.schemas.qr_generator import (
    QrCodeCreate,
    QrCodeGenerateResponse,
    QrCodeListResponse,
    QrCodeStoredResponse,
    QrCodeUpdate,
    content_preview,
)

SvgScale = 4


def generate_qr(data: QrCodeCreate) -> QrCodeGenerateResponse:
    """Validate payload, render SVG, return inline (public — no DB write)."""
    _validate_payload(data.content, data.error_level)
    svg = render_qr_svg(data.content, data.error_level)
    return QrCodeGenerateResponse(
        content_preview=content_preview(data.content),
        label=data.label,
        error_level=data.error_level,
        svg=svg,
    )


class QrLibraryService:
    """Persisted QR codes for users with ``qr-generator:read/write``."""

    def __init__(self, registry: DatabaseRegistry) -> None:
        self.registry = registry

    def _repo(self):
        if self.registry.qr_codes is None:
            msg = "QR code repository is not initialized"
            raise RuntimeError(msg)
        return self.registry.qr_codes

    @staticmethod
    def svg_url(qr_id: int) -> str:
        return f"/api/tools/qr-generator/library/{qr_id}/svg"

    def _to_response(self, doc: QrCode, *, svg: str | None = None) -> QrCodeStoredResponse:
        return QrCodeStoredResponse(
            id=doc.id,
            content=doc.content,
            content_preview=content_preview(doc.content),
            label=doc.label,
            error_level=doc.error_level,
            svg_url=self.svg_url(doc.id),
            created_at=doc.created_at,
            updated_at=doc.updated_at,
            svg=svg,
        )

    async def create_saved(
        self,
        data: QrCodeCreate,
        *,
        created_by: int,
    ) -> QrCodeStoredResponse:
        _validate_payload(data.content, data.error_level)
        doc = QrCode(
            content=data.content,
            label=data.label,
            error_level=data.error_level,
            created_by=created_by,
        )
        doc = await self._repo().insert(doc)
        svg = render_qr_svg(doc.content, doc.error_level)
        return self._to_response(doc, svg=svg)

    async def get(self, qr_id: int) -> QrCode:
        row = await self._repo().get_or_none(qr_id)
        if row is None:
            raise NotFoundError(f"QR code with id {qr_id} not found")
        return row

    def _assert_can_access(self, doc: QrCode, actor_id: int, *, is_superuser: bool) -> None:
        if is_superuser or doc.created_by == actor_id:
            return
        raise ApiError(403, "You do not have permission to access this QR code")

    async def get_stored(
        self,
        qr_id: int,
        *,
        actor_id: int,
        is_superuser: bool = False,
    ) -> QrCodeStoredResponse:
        doc = await self.get(qr_id)
        self._assert_can_access(doc, actor_id, is_superuser=is_superuser)
        return self._to_response(doc)

    async def list_library(
        self,
        *,
        actor_id: int,
        is_superuser: bool = False,
        page: int = 1,
        per_page: int = DEFAULT_PER_PAGE,
    ) -> QrCodeListResponse:
        offset, limit = paginate_params(page, per_page)
        filters: dict[str, int] = {}
        if not is_superuser:
            filters["created_by"] = actor_id
        rows = await self._repo().list(
            offset=offset,
            limit=limit,
            sort=[("created_at", -1)],
            **filters,
        )
        total = await self._repo().count(**filters)
        items = [self._to_response(row) for row in rows]
        return build_paginated(items, total=total, page=page, per_page=per_page)

    async def update_saved(
        self,
        qr_id: int,
        data: QrCodeUpdate,
        *,
        actor_id: int,
        is_superuser: bool = False,
    ) -> QrCodeStoredResponse:
        doc = await self.get(qr_id)
        self._assert_can_access(doc, actor_id, is_superuser=is_superuser)
        fields = data.model_dump(exclude_unset=True)
        if not fields:
            raise ApiError(422, "No fields to update")
        content = fields.get("content", doc.content)
        error_level = fields.get("error_level", doc.error_level)
        _validate_payload(content, error_level)
        doc = await self._repo().update_fields(qr_id, **fields)
        svg = render_qr_svg(doc.content, doc.error_level)
        return self._to_response(doc, svg=svg)

    async def render_svg(
        self,
        qr_id: int,
        *,
        actor_id: int,
        is_superuser: bool = False,
    ) -> str:
        doc = await self.get(qr_id)
        self._assert_can_access(doc, actor_id, is_superuser=is_superuser)
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
