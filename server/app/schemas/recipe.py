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

# Align with client RECIPE_TAG_LIMIT and keep list payloads bounded.
RECIPE_LIST_MAX_ITEMS = 50
RECIPE_INGREDIENT_MAX_LENGTH = 255
RECIPE_STEP_MAX_LENGTH = 1000
RECIPE_TAG_MAX_ITEMS = 6
RECIPE_TAG_MAX_LENGTH = 64
RECIPE_NOTES_MAX_LENGTH = 5000


def _https_image_only(value: HttpUrl | None) -> HttpUrl | None:
    if value is not None and value.scheme != "https":
        msg = "image_url must use https"
        raise ValueError(msg)
    return value


def _clean_ingredients(value: list[str]) -> list[str]:
    return validate_clean_string_list(
        value,
        item_max_length=RECIPE_INGREDIENT_MAX_LENGTH,
        field_name="Ingredient",
    )


def _clean_steps(value: list[str]) -> list[str]:
    return validate_clean_string_list(
        value,
        item_max_length=RECIPE_STEP_MAX_LENGTH,
        field_name="Step",
    )


def _clean_tags(value: list[str]) -> list[str]:
    if not value:
        return value
    return validate_clean_string_list(
        value,
        item_max_length=RECIPE_TAG_MAX_LENGTH,
        field_name="Tag",
    )


class RecipeFields(BaseModel):
    """Shared recipe field sanitization for create and update payloads."""

    notes: str | None = None
    image_url: HttpUrl | None = None
    prep_time: int | None = Field(None, ge=0)
    cook_time: int | None = Field(None, ge=0)
    servings: int | None = Field(None, ge=1)

    @field_validator("notes")
    @classmethod
    def clean_notes(cls, value: str | None) -> str | None:
        return validate_clean_optional(value, max_length=RECIPE_NOTES_MAX_LENGTH)

    @field_validator("image_url")
    @classmethod
    def https_image_only(cls, value: HttpUrl | None) -> HttpUrl | None:
        return _https_image_only(value)


class RecipeCreate(RecipeFields):
    title: str = Field(min_length=1, max_length=255)
    ingredients: list[str] = Field(min_length=1, max_length=RECIPE_LIST_MAX_ITEMS)
    steps: list[str] = Field(min_length=1, max_length=RECIPE_LIST_MAX_ITEMS)
    tags: list[str] = Field(default_factory=list, max_length=RECIPE_TAG_MAX_ITEMS)

    @field_validator("title")
    @classmethod
    def clean_title(cls, value: str) -> str:
        return validate_clean_required(value, max_length=255, field_name="Title")

    @field_validator("ingredients")
    @classmethod
    def clean_ingredients(cls, value: list[str]) -> list[str]:
        return _clean_ingredients(value)

    @field_validator("steps")
    @classmethod
    def clean_steps(cls, value: list[str]) -> list[str]:
        return _clean_steps(value)

    @field_validator("tags")
    @classmethod
    def clean_tags(cls, value: list[str]) -> list[str]:
        return _clean_tags(value)


class RecipeUpdate(RecipeFields):
    title: str | None = Field(None, min_length=1, max_length=255)
    ingredients: list[str] | None = Field(
        None,
        min_length=1,
        max_length=RECIPE_LIST_MAX_ITEMS,
    )
    steps: list[str] | None = Field(
        None,
        min_length=1,
        max_length=RECIPE_LIST_MAX_ITEMS,
    )
    tags: list[str] | None = Field(None, max_length=RECIPE_TAG_MAX_ITEMS)

    @field_validator("title")
    @classmethod
    def clean_title(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return validate_clean_required(value, max_length=255, field_name="Title")

    @field_validator("ingredients")
    @classmethod
    def clean_ingredients(cls, value: list[str] | None) -> list[str] | None:
        if value is None:
            return None
        return _clean_ingredients(value)

    @field_validator("steps")
    @classmethod
    def clean_steps(cls, value: list[str] | None) -> list[str] | None:
        if value is None:
            return None
        return _clean_steps(value)

    @field_validator("tags")
    @classmethod
    def clean_tags(cls, value: list[str] | None) -> list[str] | None:
        if value is None:
            return None
        return _clean_tags(value)


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
