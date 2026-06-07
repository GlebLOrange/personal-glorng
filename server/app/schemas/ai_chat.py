from pydantic import BaseModel, Field, field_validator

from app.core.text import sanitize_required_text


class ChatMessage(BaseModel):
    role: str = Field(pattern=r"^(user|assistant)$")
    content: str = Field(min_length=1, max_length=10_000)

    @field_validator("content")
    @classmethod
    def validate_content(cls, value: str) -> str:
        try:
            return sanitize_required_text(value)
        except ValueError as exc:
            msg = "Message content must not be empty"
            raise ValueError(msg) from exc


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(min_length=1, max_length=50)
