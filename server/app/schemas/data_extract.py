"""Schemas for data extraction API."""

from typing import Any, Literal

from pydantic import BaseModel, Field


class ExtractionResultResponse(BaseModel):
    format: Literal["csv", "json", "xml"]
    records: list[Any]
    meta: dict[str, Any] = Field(default_factory=dict)
