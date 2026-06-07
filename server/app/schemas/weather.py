from pydantic import BaseModel, Field, field_validator

from app.schemas.validators import validate_clean_optional, validate_clean_required


class WeatherLocationCreate(BaseModel):
    label: str = Field(default="", max_length=100)
    query: str = Field(min_length=1, max_length=100)

    @field_validator("label")
    @classmethod
    def clean_label(cls, value: str) -> str:
        return validate_clean_optional(value, max_length=100) or ""

    @field_validator("query")
    @classmethod
    def clean_query(cls, value: str) -> str:
        return validate_clean_required(value, max_length=100, field_name="Query")


class WeatherLocationReorder(BaseModel):
    ordered_ids: list[int] = Field(min_length=1)


class WeatherLocationResponse(BaseModel):
    id: int
    label: str
    query: str
    sort_order: int

    model_config = {"from_attributes": True}
