"""Data extraction service."""

from __future__ import annotations

from typing import Literal

from app.core.data_extractor import extract
from app.core.data_extractor.profiles import apply_profile
from app.core.data_extractor.types import ExtractionResult, ExtractOptions
from app.core.logging import logger

MAX_EXTRACT_SIZE = 10 * 1024 * 1024


def build_extract_options(
    *,
    profile: str | None = None,
    row_tag: str | None = None,
    xml_mode: Literal["rows", "tree"] | None = None,
    field_delimiter: str | None = None,
    list_delimiter: str | None = None,
    field_names: list[str] | None = None,
) -> ExtractOptions:
    """Build extraction options with optional profile defaults."""
    options = ExtractOptions(
        row_tag=row_tag,
        xml_mode=xml_mode or "rows",
    )
    if field_delimiter is not None:
        options.field_delimiter = field_delimiter
    if list_delimiter is not None:
        options.list_delimiter = list_delimiter
    if field_names is not None:
        options.field_names = field_names
    return apply_profile(profile, options)


def extract_upload(
    contents: bytes,
    *,
    filename: str,
    format: str | None = None,
    options: ExtractOptions | None = None,
) -> ExtractionResult:
    """Parse an uploaded file into structured records."""
    opts = options or ExtractOptions()
    logger.info(
        "Extracting uploaded file",
        context={"filename": filename, "profile": opts.profile},
    )
    return extract(
        contents,
        format,
        filename=filename,
        options=opts,
    )
