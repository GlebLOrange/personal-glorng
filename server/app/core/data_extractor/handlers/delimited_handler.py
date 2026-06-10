"""Delimited text extraction (pipe, custom separators)."""

from __future__ import annotations

from typing import Any

from app.core.data_extractor.profiles import transform_record
from app.core.data_extractor.types import ExtractOptions

HandlerResult = tuple[list[Any], dict[str, Any]]


def extract_delimited(content: str, options: ExtractOptions) -> HandlerResult:
    if not content.strip():
        return [], {"row_count": 0, "columns": [], "error_rows": []}

    records: list[dict[str, Any]] = []
    error_rows: list[dict[str, Any]] = []
    columns = _column_names(options)

    for line_number, line in enumerate(content.splitlines(), start=1):
        if options.skip_empty_lines and not line.strip():
            continue
        try:
            raw_fields = line.split(options.field_delimiter)
            record = _map_fields(raw_fields, options)
            record = transform_record(options.profile, record)
            records.append(record)
        except (ValueError, TypeError) as exc:
            error_rows.append(
                {
                    "line_number": line_number,
                    "message": str(exc),
                    "raw_line": line,
                },
            )

    return records, {
        "row_count": len(records),
        "columns": columns,
        "error_rows": error_rows,
        "error_count": len(error_rows),
    }


def _column_names(options: ExtractOptions) -> list[str]:
    if options.field_names:
        return list(options.field_names)
    return []


def _map_fields(raw_fields: list[str], options: ExtractOptions) -> dict[str, Any]:
    if options.field_names:
        expected = len(options.field_names)
        if len(raw_fields) != expected:
            msg = f"Expected {expected} fields, got {len(raw_fields)}"
            raise ValueError(msg)
        names = options.field_names
    else:
        names = [f"field_{index}" for index in range(len(raw_fields))]

    record: dict[str, Any] = {}
    for name, value in zip(names, raw_fields, strict=False):
        if name in options.list_fields:
            record[name] = _split_list(value, options.list_delimiter)
        elif isinstance(value, str):
            record[name] = value.strip()
        else:
            record[name] = value
    return record


def _split_list(value: str, delimiter: str) -> list[str]:
    if not value or not value.strip():
        return []
    return [part.strip() for part in value.split(delimiter) if part.strip()]
