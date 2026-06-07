from pydantic import BaseModel, Field


class WorldTimeResponse(BaseModel):
    """Current local time for an IANA timezone."""

    timezone: str = Field(description="IANA timezone identifier (e.g. Europe/London).")
    datetime: str = Field(description="Local datetime with offset.")
    utc_datetime: str = Field(description="UTC datetime.")
    utc_offset: str = Field(description="UTC offset (e.g. +01:00).")
    unixtime: int = Field(description="Unix timestamp in seconds.")
    dst: bool = Field(description="Whether daylight saving time is active.")
    abbreviation: str = Field(description="Timezone abbreviation (e.g. BST).")
