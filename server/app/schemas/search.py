from pydantic import BaseModel, Field

from app.schemas.ai_chat import ChatMessage


class SearchSource(BaseModel):
    id: int
    title: str
    url: str
    source_type: str
    snippet: str


class SearchHit(BaseModel):
    id: int
    title: str
    url: str
    source_type: str
    snippet: str
    visibility: str


class SearchQueryResponse(BaseModel):
    query: str
    hits: list[SearchHit]


class SearchChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(min_length=1, max_length=50)


class SearchConfigResponse(BaseModel):
    enabled: bool
    configured: bool
