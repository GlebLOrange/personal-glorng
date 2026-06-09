"""Unified file data extraction entry point."""

from __future__ import annotations

from pathlib import Path

from app.core.data_extractor.format import resolve_format
from app.core.data_extractor.registry import HANDLERS
from app.core.data_extractor.types import (
    DataFormat,
    ExtractionResult,
    ExtractOptions,
)
from app.core.exceptions import ValidationError
from app.core.logging import logger

__all__ = [
    "DataFormat",
    "ExtractOptions",
    "ExtractionResult",
    "extract",
]


def extract(
    source: Path | str | bytes,
    format: DataFormat | str | None = None,
    *,
    filename: str | None = None,
    options: ExtractOptions | None = None,
) -> ExtractionResult:
    """Extract structured records from a file path or raw bytes."""
    opts = options or ExtractOptions()
    if isinstance(source, bytes) and format is None and not filename:
        raise ValidationError(
            "filename is required when source is bytes and format is omitted",
        )
    content, resolved_filename = _load_content(
        source,
        filename=filename,
        encoding=opts.encoding,
    )
    resolved_format = resolve_format(format, filename=resolved_filename)
    handler = HANDLERS.get(resolved_format)
    if handler is None:
        supported = ", ".join(f.value for f in DataFormat)
        raise ValidationError(
            f"No handler for format '{resolved_format}'. Supported: {supported}",
        )

    logger.info(
        "Extracting data",
        context={
            "format": resolved_format.value,
            "filename": resolved_filename or "<unknown>",
        },
    )
    records, meta = handler(content, opts)
    meta.setdefault("row_count", len(records))
    meta["detected_format"] = resolved_format.value
    if resolved_filename:
        meta["filename"] = resolved_filename
    return ExtractionResult(format=resolved_format, records=records, meta=meta)


def _load_content(
    source: Path | str | bytes,
    *,
    filename: str | None,
    encoding: str,
) -> tuple[str, str | None]:
    if isinstance(source, bytes):
        try:
            return source.decode(encoding), filename
        except UnicodeDecodeError as exc:
            raise ValidationError(f"File must be {encoding} encoded text") from exc

    path = Path(source)
    if not path.is_file():
        raise ValidationError(f"File not found: {path}")
    try:
        return path.read_text(encoding=encoding), filename or path.name
    except UnicodeDecodeError as exc:
        raise ValidationError(
            f"File must be {encoding} encoded text: {path}",
        ) from exc
