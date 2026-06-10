"""Schemas for data extraction and import API."""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class ExtractionResultResponse(BaseModel):
    format: Literal["csv", "json", "xml", "delimited"]
    records: list[Any]
    meta: dict[str, Any] = Field(default_factory=dict)


class ImportRowErrorResponse(BaseModel):
    line_number: int | None = None
    message: str
    raw_line: str | None = None


class ImportResultResponse(BaseModel):
    batch_id: int
    format: str
    profile: str | None = None
    row_count: int
    error_count: int
    preview: list[dict[str, Any]] = Field(default_factory=list)
    errors: list[ImportRowErrorResponse] = Field(default_factory=list)


class ImportBatchResponse(BaseModel):
    id: int
    filename: str
    format: str
    profile: str | None = None
    status: Literal["completed", "partial", "failed"]
    row_count: int
    error_count: int
    imported_by: int
    promoted_count: int = 0
    promoted_at: datetime | None = None
    meta: dict[str, Any] = Field(default_factory=dict)


class ImportBatchListResponse(BaseModel):
    items: list[ImportBatchResponse]
    total: int


class PromoteBatchResponse(BaseModel):
    batch_id: int
    promoted: int
    skipped: int
    errors: list[str] = Field(default_factory=list)


class ImportRowResponse(BaseModel):
    id: int
    batch_id: int
    row_index: int
    fields: dict[str, Any] = Field(default_factory=dict)
    raw_line: str | None = None
    error: str | None = None


class ImportBatchDetailResponse(BaseModel):
    batch: ImportBatchResponse
    preview_rows: list[ImportRowResponse] = Field(default_factory=list)
