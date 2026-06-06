from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ExpenseCategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=64)


class ExpenseCategoryUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    monthly_budget: Decimal | None = Field(None, ge=0)


class ExpenseCategoryResponse(BaseModel):
    id: int
    name: str
    sort_order: int
    monthly_budget: Decimal | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
