"""Data extraction service."""

from __future__ import annotations

from typing import Literal

from app.core.data_extractor import extract
from app.core.data_extractor.types import ExtractionResult, ExtractOptions
from app.core.logging import logger

MAX_EXTRACT_SIZE = 10 * 1024 * 1024


def extract_upload(
    contents: bytes,
    *,
    filename: str,
    format: str | None = None,
    row_tag: str | None = None,
    xml_mode: Literal["rows", "tree"] | None = None,
) -> ExtractionResult:
    options = ExtractOptions(
        row_tag=row_tag,
        xml_mode=xml_mode or "rows",
    )
    logger.info(
        "Extracting uploaded file",
        context={"filename": filename},
    )
    return extract(
        contents,
        format,
        filename=filename,
        options=options,
    )
