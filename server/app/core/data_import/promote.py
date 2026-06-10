"""Promote staged import rows into domain collections."""

from __future__ import annotations

from dataclasses import dataclass

from app.core.exceptions import ValidationError
from app.core.logging import logger
from app.db.documents.embed_item import EmbedItem
from app.db.documents.import_batch import ImportBatch
from app.db.documents.import_row import ImportRow
from app.db.repositories.embed_item import EmbedItemRepository


@dataclass
class PromoteResult:
    promoted: int
    skipped: int
    errors: list[str]


def _embed_item_from_row(batch_id: int, row: ImportRow) -> EmbedItem | None:
    fields = row.fields
    embed_id = fields.get("embed_id")
    if not isinstance(embed_id, str) or not embed_id.strip():
        return None
    return EmbedItem(
        embed_id=embed_id,
        embed_url=_optional_str(fields.get("embed_url")),
        title=_optional_str(fields.get("title")),
        thumb_url=_optional_str(fields.get("thumb_url")),
        thumb_base_url=_optional_str(fields.get("thumb_base_url")),
        preview_urls=_str_list(fields.get("preview_urls")),
        tags=_str_list(fields.get("tags")),
        categories=_str_list(fields.get("categories")),
        performers=_str_list(fields.get("performers")),
        channel=_optional_str(fields.get("channel")),
        duration_sec=_optional_int(fields.get("duration_sec")),
        view_count=_optional_int(fields.get("view_count")),
        upvote_count=_optional_int(fields.get("upvote_count")),
        downvote_count=_optional_int(fields.get("downvote_count")),
        rating_percent=_optional_float(fields.get("rating_percent")),
        source_batch_id=batch_id,
        source_row_id=row.id,
        raw_fields=dict(fields),
    )


def _optional_str(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _optional_int(value: object) -> int | None:
    if value is None or value == "":
        return None
    if isinstance(value, int):
        return value
    return int(str(value).strip())


def _optional_float(value: object) -> float | None:
    if value is None or value == "":
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return float(str(value).strip())


def _str_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if item]


async def promote_batch_rows(
    batch: ImportBatch,
    rows: list[ImportRow],
    embed_repo: EmbedItemRepository,
) -> PromoteResult:
    """Promote staged rows based on the batch profile."""
    profile = batch.profile
    if profile != "pipe_embed":
        msg = f"Promotion is not supported for profile '{profile or 'none'}'"
        raise ValidationError(msg)

    promoted = 0
    skipped = 0
    errors: list[str] = []

    for row in rows:
        if row.error:
            skipped += 1
            continue
        try:
            item = _embed_item_from_row(batch.id, row)
            if item is None:
                skipped += 1
                continue
            await embed_repo.upsert_by_embed_id(item)
            promoted += 1
        except (TypeError, ValueError) as exc:
            errors.append(f"row {row.row_index}: {exc}")
            logger.warning(
                "Failed to promote import row",
                context={"batch_id": batch.id, "row_index": row.row_index},
            )

    logger.info(
        "Import batch promoted",
        context={
            "batch_id": batch.id,
            "profile": profile,
            "promoted": promoted,
            "skipped": skipped,
            "errors": len(errors),
        },
    )
    return PromoteResult(promoted=promoted, skipped=skipped, errors=errors)
