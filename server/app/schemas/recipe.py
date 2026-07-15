from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator

from app.schemas.common import PaginatedResponse
from app.schemas.validators import (
    validate_clean_optional,
    validate_clean_required,
    validate_clean_string_list,
)

RecipeSort = Literal[
    "title_asc",
    "title_desc",
    "prep_asc",
    "total_time_asc",
]


class RecipeCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    ingredients: list[str] = Field(min_length=1)
    steps: list[str] = Field(min_length=1)
    notes: str | None = None
    tags: list[str] = Field(default_factory=list)
    image_url: HttpUrl | None = None
    prep_time: int | None = Field(None, ge=0)
    cook_time: int | None = Field(None, ge=0)
    servings: int | None = Field(None, ge=1)

    @field_validator("title")
    @classmethod
    def clean_title(cls, value: str) -> str:
        return validate_clean_required(value, max_length=255, field_name="Title")

    @field_validator("ingredients", "steps")
    @classmethod
    def clean_list_fields(cls, value: list[str]) -> list[str]:
        return validate_clean_string_list(value, field_name="Item")

    @field_validator("notes")
    @classmethod
    def clean_notes(cls, value: str | None) -> str | None:
        return validate_clean_optional(value)

    @field_validator("tags")
    @classmethod
    def clean_tags(cls, value: list[str]) -> list[str]:
        if not value:
            return value
        return validate_clean_string_list(value, item_max_length=64, field_name="Tag")

    @field_validator("image_url")
    @classmethod
    def https_image_only(cls, value: HttpUrl | None) -> HttpUrl | None:
        if value is not None and value.scheme != "https":
            msg = "image_url must use https"
            raise ValueError(msg)
        return value


class RecipeUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    ingredients: list[str] | None = Field(None, min_length=1)
    steps: list[str] | None = Field(None, min_length=1)
    notes: str | None = None
    tags: list[str] | None = None
    image_url: HttpUrl | None = None
    prep_time: int | None = Field(None, ge=0)
    cook_time: int | None = Field(None, ge=0)
    servings: int | None = Field(None, ge=1)

    @field_validator("title")
    @classmethod
    def clean_title(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return validate_clean_required(value, max_length=255, field_name="Title")

    @field_validator("ingredients", "steps")
    @classmethod
    def clean_list_fields(cls, value: list[str] | None) -> list[str] | None:
        if value is None:
            return None
        return validate_clean_string_list(value, field_name="Item")

    @field_validator("notes")
    @classmethod
    def clean_notes(cls, value: str | None) -> str | None:
        return validate_clean_optional(value)

    @field_validator("tags")
    @classmethod
    def clean_tags(cls, value: list[str] | None) -> list[str] | None:
        if value is None:
            return None
        if not value:
            return value
        return validate_clean_string_list(value, item_max_length=64, field_name="Tag")

    @field_validator("image_url")
    @classmethod
    def https_image_only(cls, value: HttpUrl | None) -> HttpUrl | None:
        if value is not None and value.scheme != "https":
            msg = "image_url must use https"
            raise ValueError(msg)
        return value


class RecipeResponse(BaseModel):
    id: int
    title: str
    ingredients: list[str]
    steps: list[str]
    notes: str | None
    tags: list[str]
    image_url: str | None
    prep_time: int | None
    cook_time: int | None
    servings: int | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RecipeListResponse(PaginatedResponse[RecipeResponse]):
    pass
