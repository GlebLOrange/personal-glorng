"""Format detection from explicit values and file extensions."""

from __future__ import annotations

from pathlib import Path

from app.core.data_extractor.types import DataFormat
from app.core.exceptions import ValidationError

_EXTENSION_MAP: dict[str, DataFormat] = {
    ".csv": DataFormat.CSV,
    ".tsv": DataFormat.CSV,
    ".json": DataFormat.JSON,
    ".xml": DataFormat.XML,
    ".txt": DataFormat.DELIMITED,
    ".pipe": DataFormat.DELIMITED,
}


def parse_format(value: DataFormat | str | None) -> DataFormat | None:
    if value is None:
        return None
    if isinstance(value, DataFormat):
        return value
    normalized = value.strip().lower()
    try:
        return DataFormat(normalized)
    except ValueError as exc:
        supported = ", ".join(f.value for f in DataFormat)
        raise ValidationError(
            f"Unsupported format '{value}'. Supported: {supported}",
        ) from exc


def sniff_format(filename: str | None) -> DataFormat:
    if not filename:
        raise ValidationError("filename is required to detect format")
    suffix = Path(filename).suffix.lower()
    detected = _EXTENSION_MAP.get(suffix)
    if detected is None:
        supported = ", ".join(sorted(_EXTENSION_MAP))
        raise ValidationError(
            f"Cannot detect format from '{filename}'. "
            f"Supported extensions: {supported}",
        )
    return detected


def resolve_format(
    format: DataFormat | str | None,
    *,
    filename: str | None,
) -> DataFormat:
    explicit = parse_format(format)
    if explicit is not None:
        return explicit
    return sniff_format(filename)
