from pydantic import BaseModel, Field, field_validator

from app.services.ai_chat import DEFAULT_PROVIDER, sanitize_content


class ChatMessage(BaseModel):
    role: str = Field(pattern=r"^(user|assistant)$")
    content: str = Field(min_length=1, max_length=10_000)

    @field_validator("content")
    @classmethod
    def validate_content(cls, value: str) -> str:
        return sanitize_content(value)


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(min_length=1, max_length=50)
    provider: str = Field(default=DEFAULT_PROVIDER, pattern=r"^groq$")
    model: str | None = None


class ChatResponse(BaseModel):
    reply: str
    model: str
    usage: dict[str, int]


class ProviderInfo(BaseModel):
    id: str
    models: list[str]
    default_model: str
