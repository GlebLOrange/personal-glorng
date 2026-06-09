"""JSON file extraction."""

from __future__ import annotations

import json
from typing import Any

from app.core.data_extractor.types import ExtractOptions
from app.core.exceptions import ValidationError

HandlerResult = tuple[list[Any], dict[str, Any]]


def extract_json(content: str, options: ExtractOptions) -> HandlerResult:
    del options
    if not content.strip():
        return [], {"row_count": 0}

    try:
        parsed = json.loads(content)
    except json.JSONDecodeError as exc:
        raise ValidationError(f"Invalid JSON: {exc.msg}") from exc

    return _normalize_json(parsed)


def _normalize_json(parsed: object) -> HandlerResult:
    if isinstance(parsed, list):
        if not parsed:
            return [], {"row_count": 0}
        if all(isinstance(item, dict) for item in parsed):
            columns = _collect_columns(parsed)
            return parsed, {"row_count": len(parsed), "columns": columns}
        value_type = type(parsed[0]).__name__
        records = [{"value": item} for item in parsed]
        return records, {
            "row_count": len(records),
            "value_type": value_type,
            "columns": ["value"],
        }

    if isinstance(parsed, dict):
        columns = sorted(parsed)
        return [parsed], {"row_count": 1, "columns": columns}

    records = [{"value": parsed}]
    return records, {
        "row_count": 1,
        "value_type": type(parsed).__name__,
        "columns": ["value"],
    }


def _collect_columns(records: list[dict[str, Any]]) -> list[str]:
    columns: list[str] = []
    seen: set[str] = set()
    for record in records:
        for key in record:
            if key not in seen:
                seen.add(key)
                columns.append(key)
    return columns
