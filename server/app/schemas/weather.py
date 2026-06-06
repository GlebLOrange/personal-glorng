from pydantic import BaseModel, Field


class WeatherLocationCreate(BaseModel):
    label: str = Field(default="", max_length=100)
    query: str = Field(min_length=1, max_length=100)


class WeatherLocationReorder(BaseModel):
    ordered_ids: list[int] = Field(min_length=1)


class WeatherLocationResponse(BaseModel):
    id: int
    label: str
    query: str
    sort_order: int

    model_config = {"from_attributes": True}
