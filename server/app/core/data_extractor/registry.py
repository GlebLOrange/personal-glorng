"""Dispatch table for format handlers."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from app.core.data_extractor.handlers import (
    extract_csv,
    extract_delimited,
    extract_json,
    extract_xml,
)
from app.core.data_extractor.types import DataFormat, ExtractOptions

Handler = Callable[[str, ExtractOptions], tuple[list[Any], dict[str, Any]]]

HANDLERS: dict[DataFormat, Handler] = {
    DataFormat.CSV: extract_csv,
    DataFormat.JSON: extract_json,
    DataFormat.XML: extract_xml,
    DataFormat.DELIMITED: extract_delimited,
}
