"""QR code generation (Segno) — public ephemeral + owner library."""

import segno
from segno import DataOverflowError

from app.core.exceptions import ApiError, NotFoundError
from app.core.pagination import build_paginated
from app.core.utils import DEFAULT_PER_PAGE, paginate_params
from app.db.documents.qr_code import QrCode, QrErrorLevel
from app.db.registry import DatabaseRegistry
from app.db.repositories.qr_code import QrCodeRepository
from app.schemas.qr_generator import (
    QrCodeCreate,
    QrCodeGenerateResponse,
    QrCodeListItem,
    QrCodeListResponse,
    QrCodeStoredResponse,
    QrCodeUpdate,
    content_preview,
)
from app.services.audit import AuditService

SvgScale = 4


def generate_qr(data: QrCodeCreate) -> QrCodeGenerateResponse:
    """Render SVG inline (public — no DB write)."""
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

    def _repo(self) -> QrCodeRepository:
        if self.registry.qr_codes is None:
            msg = "QR code repository is not initialized"
            raise RuntimeError(msg)
        return self.registry.qr_codes

    @staticmethod
    def svg_url(qr_id: int) -> str:
        return f"/api/tools/qr-generator/library/{qr_id}/svg"

    def _to_list_item(self, doc: QrCode) -> QrCodeListItem:
        return QrCodeListItem(
            id=doc.id,
            content_preview=content_preview(doc.content),
            label=doc.label,
            error_level=doc.error_level,
            svg_url=self.svg_url(doc.id),
            created_at=doc.created_at,
            updated_at=doc.updated_at,
        )

    def _to_response(
        self, doc: QrCode, *, svg: str | None = None
    ) -> QrCodeStoredResponse:
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
        svg = render_qr_svg(data.content, data.error_level)
        doc = QrCode(
            content=data.content,
            label=data.label,
            error_level=data.error_level,
            created_by=created_by,
        )
        doc = await self._repo().insert(doc)
        await AuditService(self.registry).record_domain(
            action="qr.created",
            resource_type="qr",
            resource_id=doc.id,
            actor_id=created_by,
            metadata={"label": doc.label, "error_level": doc.error_level},
        )
        return self._to_response(doc, svg=svg)

    async def get(self, qr_id: int) -> QrCode:
        row = await self._repo().get_or_none(qr_id)
        if row is None:
            raise NotFoundError(f"QR code with id {qr_id} not found")
        return row

    def _assert_can_access(
        self, doc: QrCode, actor_id: int, *, is_superuser: bool
    ) -> None:
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
        svg = render_qr_svg(doc.content, doc.error_level)
        return self._to_response(doc, svg=svg)

    async def list_by_owner(
        self,
        *,
        created_by: int,
        page: int = 1,
        per_page: int = DEFAULT_PER_PAGE,
    ) -> QrCodeListResponse:
        """List QR codes owned by ``created_by`` (url-shortener-style owner scope)."""
        offset, limit = paginate_params(page, per_page)
        rows = await self._repo().list(
            offset=offset,
            limit=limit,
            created_by=created_by,
            sort=[("created_at", -1)],
        )
        total = await self._repo().count(created_by=created_by)
        items = [self._to_list_item(row) for row in rows]
        return build_paginated(
            items,
            total=total,
            page=page,
            per_page=limit,
        )

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
        svg = render_qr_svg(content, error_level)
        doc = await self._repo().update_fields(qr_id, **fields)
        await AuditService(self.registry).record_domain(
            action="qr.updated",
            resource_type="qr",
            resource_id=qr_id,
            actor_id=actor_id,
            metadata={"label": doc.label, "error_level": doc.error_level},
        )
        return self._to_response(doc, svg=svg)

    async def delete_saved(
        self,
        qr_id: int,
        *,
        actor_id: int,
        is_superuser: bool = False,
    ) -> None:
        doc = await self.get(qr_id)
        self._assert_can_access(doc, actor_id, is_superuser=is_superuser)
        await self._repo().delete(qr_id)
        await AuditService(self.registry).record_domain(
            action="qr.deleted",
            resource_type="qr",
            resource_id=qr_id,
            actor_id=actor_id,
        )

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


def render_qr_svg(content: str, error_level: QrErrorLevel) -> str:
    """Validate payload and render a QR code as an SVG string (one segno.make)."""
    try:
        qr = segno.make(content, error=error_level)
    except (ValueError, DataOverflowError) as exc:
        raise ApiError(
            422,
            "Content is too long for the selected error correction level",
        ) from exc
    svg = qr.svg_inline(scale=SvgScale, border=2)
    # segno omits xmlns; required for standalone img/data: and downloaded .svg files
    if "xmlns=" not in svg:
        svg = svg.replace("<svg", '<svg xmlns="http://www.w3.org/2000/svg"', 1)
    return svg
