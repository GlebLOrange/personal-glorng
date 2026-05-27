from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str = Field(pattern=r"^(user|assistant|system)$")
    content: str = Field(min_length=1, max_length=10_000)


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(min_length=1, max_length=50)
    provider: str = "deepseek"
    model: str | None = None


class ChatResponse(BaseModel):
    reply: str
    model: str
    usage: dict[str, int]


class ProviderInfo(BaseModel):
    id: str
    models: list[str]
    default_model: str
