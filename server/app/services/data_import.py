"""Persist extracted file rows to staging collections."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Literal

from app.core.data_extractor.types import ExtractOptions
from app.core.data_import.promote import PromoteResult, promote_batch_rows
from app.core.exceptions import ApiError
from app.core.logging import logger
from app.core.permissions import SUPERUSER_PERMISSION, user_has_permission
from app.db.documents.import_batch import ImportBatch
from app.db.documents.import_row import ImportRow
from app.db.documents.user import User
from app.db.registry import DatabaseRegistry
from app.db.repositories.data_import import DataImportRepository
from app.db.repositories.embed_item import EmbedItemRepository
from app.services.audit import AuditService
from app.services.data_extract import extract_upload

PREVIEW_LIMIT = 10
PROMOTE_BATCH_SIZE = 500


@dataclass
class ImportResult:
    batch_id: int
    format: str
    profile: str | None
    row_count: int
    error_count: int
    preview: list[dict[str, Any]] = field(default_factory=list)
    errors: list[dict[str, Any]] = field(default_factory=list)


def _batch_status(
    row_count: int, error_count: int
) -> Literal["completed", "partial", "failed"]:
    if row_count == 0 and error_count > 0:
        return "failed"
    if error_count > 0:
        return "partial"
    return "completed"


def _imports(registry: DatabaseRegistry) -> DataImportRepository:
    if registry.data_imports is None:
        msg = "Data import repository is not initialized"
        raise RuntimeError(msg)
    return registry.data_imports


def _embed_items(registry: DatabaseRegistry) -> EmbedItemRepository:
    db = registry.require_mongo()
    return EmbedItemRepository(db)


def assert_batch_access(batch: ImportBatch, user: User) -> None:
    """Ensure the user may read or mutate the given import batch."""
    if user_has_permission(user, SUPERUSER_PERMISSION):
        return
    if batch.imported_by != user.id:
        logger.warning(
            "Import batch access denied",
            context={"batch_id": batch.id, "user_id": user.id},
        )
        raise ApiError(403, "You do not have permission to access this import batch")


def _build_import_rows(
    batch_id: int,
    records: list[Any],
    error_rows: list[dict[str, Any]],
) -> list[ImportRow]:
    import_rows: list[ImportRow] = []
    for index, record in enumerate(records):
        fields = record if isinstance(record, dict) else {"value": record}
        import_rows.append(
            ImportRow(batch_id=batch_id, row_index=index, fields=fields),
        )
    for error in error_rows:
        import_rows.append(
            ImportRow(
                batch_id=batch_id,
                row_index=len(import_rows),
                fields={},
                raw_line=error.get("raw_line"),
                error=str(error.get("message", "Parse error")),
            ),
        )
    return import_rows


async def _persist_import_rows(
    repo: DataImportRepository,
    batch: ImportBatch,
    import_rows: list[ImportRow],
) -> None:
    try:
        await repo.rows.insert_many(import_rows)
    except Exception:
        logger.error(
            "Import row persistence failed; rolling back batch",
            context={"batch_id": batch.id, "row_count": len(import_rows)},
        )
        await repo.delete_batch(batch.id)
        raise


async def import_upload(
    registry: DatabaseRegistry,
    *,
    contents: bytes,
    filename: str,
    user_id: int,
    format: str | None = None,
    options: ExtractOptions | None = None,
) -> ImportResult:
    """Extract an upload and persist rows to staging storage."""
    opts = options or ExtractOptions()
    result = await asyncio.to_thread(
        extract_upload,
        contents,
        filename=filename,
        format=format,
        options=opts,
    )
    error_rows: list[dict[str, Any]] = list(result.meta.get("error_rows") or [])
    error_count = len(error_rows)

    batch = ImportBatch(
        filename=filename,
        format=result.format.value,
        profile=opts.profile,
        status=_batch_status(len(result.records), error_count),
        row_count=len(result.records),
        error_count=error_count,
        imported_by=user_id,
        meta=dict(result.meta),
    )
    repo = _imports(registry)
    batch = await repo.batches.insert(batch)
    import_rows = await asyncio.to_thread(
        _build_import_rows,
        batch.id,
        result.records,
        error_rows,
    )
    await _persist_import_rows(repo, batch, import_rows)

    preview = [row.fields for row in import_rows if not row.error][:PREVIEW_LIMIT]

    await AuditService(registry).record_domain(
        action="data-import.completed",
        resource_type="import_batch",
        resource_id=batch.id,
        actor_id=user_id,
        metadata={
            "filename": filename,
            "format": result.format.value,
            "profile": opts.profile,
            "row_count": batch.row_count,
            "error_count": batch.error_count,
        },
    )

    logger.info(
        "Import batch persisted",
        context={
            "batch_id": batch.id,
            "row_count": batch.row_count,
            "error_count": batch.error_count,
        },
    )

    return ImportResult(
        batch_id=batch.id,
        format=result.format.value,
        profile=opts.profile,
        row_count=batch.row_count,
        error_count=batch.error_count,
        preview=preview,
        errors=error_rows,
    )


@dataclass
class BatchListResult:
    items: list[ImportBatch]
    total: int


async def list_batches(
    registry: DatabaseRegistry,
    user: User,
    *,
    offset: int = 0,
    limit: int = 20,
) -> BatchListResult:
    """List import batches visible to the user."""
    repo = _imports(registry)
    if user_has_permission(user, SUPERUSER_PERMISSION):
        items = await repo.batches.list(
            offset=offset,
            limit=limit,
            sort=[("created_at", -1)],
        )
        total = await repo.batches.count()
        return BatchListResult(items=items, total=total)
    items = await repo.batches.list_for_user(
        user.id,
        offset=offset,
        limit=limit,
    )
    total = await repo.batches.count_for_user(user.id)
    return BatchListResult(items=items, total=total)


async def get_batch_summary(
    registry: DatabaseRegistry,
    batch_id: int,
    user: User,
    *,
    preview_limit: int = PREVIEW_LIMIT,
) -> tuple[ImportBatch, list[ImportRow]]:
    """Load a batch and preview rows after an ownership check."""
    repo = _imports(registry)
    batch = await repo.batches.get(batch_id)
    assert_batch_access(batch, user)
    rows = await repo.rows.list_for_batch(batch_id, limit=preview_limit)
    return batch, rows


async def promote_batch(
    registry: DatabaseRegistry,
    batch_id: int,
    user: User,
) -> PromoteResult:
    """Promote staged rows from a batch into domain collections."""
    repo = _imports(registry)
    batch = await repo.batches.get(batch_id)
    assert_batch_access(batch, user)
    embed_repo = _embed_items(registry)
    result = PromoteResult(promoted=0, skipped=0, errors=[])
    after_row_index: int | None = None
    while True:
        rows = await repo.rows.list_success_for_batch(
            batch_id,
            after_row_index=after_row_index,
            limit=PROMOTE_BATCH_SIZE,
        )
        if not rows:
            break
        chunk_result = await promote_batch_rows(batch, rows, embed_repo)
        result.promoted += chunk_result.promoted
        result.skipped += chunk_result.skipped
        result.errors.extend(chunk_result.errors)
        after_row_index = rows[-1].row_index

    if result.promoted > 0:
        await repo.batches.update_fields(
            batch_id,
            promoted_count=batch.promoted_count + result.promoted,
            promoted_at=datetime.now(UTC),
        )
        await AuditService(registry).record_domain(
            action="data-import.promoted",
            resource_type="import_batch",
            resource_id=batch_id,
            actor_id=user.id,
            metadata={
                "profile": batch.profile,
                "promoted": result.promoted,
                "skipped": result.skipped,
                "errors": len(result.errors),
            },
        )
    return result
