"""Schemas for data extraction and import API."""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import PaginatedResponse


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

    model_config = ConfigDict(from_attributes=True)


class ImportBatchListResponse(PaginatedResponse[ImportBatchResponse]):
    """Paginated import batch list."""


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

    model_config = ConfigDict(from_attributes=True)


class ImportBatchDetailResponse(BaseModel):
    batch: ImportBatchResponse
    preview_rows: list[ImportRowResponse] = Field(default_factory=list)
