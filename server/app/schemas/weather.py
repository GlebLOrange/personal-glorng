from pydantic import BaseModel, Field


class WeatherCityUpdate(BaseModel):
    city: str = Field(min_length=1, max_length=100)


class WeatherConfigResponse(BaseModel):
    city: str
