from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.schemas.validators import validate_clean_required


class FeedbackCreate(BaseModel):
    email: EmailStr
    theme: str = Field(min_length=1, max_length=255)
    message: str = Field(min_length=1, max_length=5000)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "visitor@example.com",
                "theme": "Portfolio",
                "message": "Great site — love the search feature.",
            }
        }
    )

    @field_validator("theme")
    @classmethod
    def clean_theme(cls, value: str) -> str:
        return validate_clean_required(value, max_length=255, field_name="Theme")

    @field_validator("message")
    @classmethod
    def clean_message(cls, value: str) -> str:
        return validate_clean_required(value, max_length=5000, field_name="Message")


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
