from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class FeedbackCreate(BaseModel):
    email: EmailStr
    theme: str = Field(min_length=1, max_length=255)
    message: str = Field(min_length=1, max_length=5000)


class FeedbackStatusUpdate(BaseModel):
    status: str = Field(pattern=r"^(read|archived)$")


class FeedbackResponse(BaseModel):
    id: int
    email: str
    theme: str
    message: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
