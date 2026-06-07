import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.permissions import validate_permissions


class AdminUserSummary(BaseModel):
    id: uuid.UUID = Field(validation_alias="public_id")
    email: str
    display_name: str | None = None
    is_verified: bool
    permissions: list[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class UpdateUserPermissionsRequest(BaseModel):
    permissions: list[str]

    @field_validator("permissions")
    @classmethod
    def check_permissions(cls, value: list[str]) -> list[str]:
        return validate_permissions(value)
