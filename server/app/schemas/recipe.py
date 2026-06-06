from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator


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

    @field_validator("image_url")
    @classmethod
    def https_image_only(cls, value: HttpUrl | None) -> HttpUrl | None:
        if value is not None and value.scheme != "https":
            msg = "image_url must use https"
            raise ValueError(msg)
        return value


class RecipeUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    ingredients: list[str] | None = None
    steps: list[str] | None = None
    notes: str | None = None
    tags: list[str] | None = None
    image_url: HttpUrl | None = None
    prep_time: int | None = Field(None, ge=0)
    cook_time: int | None = Field(None, ge=0)
    servings: int | None = Field(None, ge=1)

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
