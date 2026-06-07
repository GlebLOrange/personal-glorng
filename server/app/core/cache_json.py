import json
from typing import Any


def safe_cache_json_loads(raw: str) -> Any | None:
    """Parse Redis cache JSON; return None when corrupt."""
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return None
