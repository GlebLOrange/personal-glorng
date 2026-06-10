"""Shared types for file data extraction."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Literal


class DataFormat(StrEnum):
    CSV = "csv"
    JSON = "json"
    XML = "xml"
    DELIMITED = "delimited"


XmlMode = Literal["rows", "tree"]


@dataclass
class ExtractOptions:
    encoding: str = "utf-8"
    csv_delimiter: str | None = None
    xml_mode: XmlMode = "rows"
    row_tag: str | None = None
    profile: str | None = None
    line_delimiter: str = "\n"
    field_delimiter: str = "|"
    list_delimiter: str = ";"
    field_names: list[str] | None = None
    list_fields: frozenset[str] = field(default_factory=frozenset)
    skip_empty_lines: bool = True


@dataclass
class ExtractionResult:
    format: DataFormat
    records: list[Any]
    meta: dict[str, Any] = field(default_factory=dict)
