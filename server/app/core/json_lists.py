"""Shared JSON-encoded string list parsing."""

import json

from app.core.exceptions import ApiError


def parse_json_string_list(
    raw: str,
    *,
    strict: bool = False,
    field: str = "field",
) -> list[str]:
    """Parse a JSON array of strings from stored text."""
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        if strict:
            raise ApiError(
                500,
                f"Recipe {field} data is corrupted",
                is_operational=False,
            ) from exc
        return []
    if not isinstance(value, list):
        if strict:
            raise ApiError(
                500,
                f"Recipe {field} data is corrupted",
                is_operational=False,
            )
        return []
    return [str(item) for item in value]
