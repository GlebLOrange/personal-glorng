from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.validators import validate_clean_required


class ExpenseCategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=64)

    @field_validator("name")
    @classmethod
    def clean_name(cls, value: str) -> str:
        return validate_clean_required(value, max_length=64, field_name="Name")


class ExpenseCategoryUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    monthly_budget: Decimal | None = Field(None, ge=0)

    @field_validator("name")
    @classmethod
    def clean_name(cls, value: str) -> str:
        return validate_clean_required(value, max_length=64, field_name="Name")


class ExpenseCategoryResponse(BaseModel):
    id: int
    name: str
    sort_order: int
    monthly_budget: Decimal | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
