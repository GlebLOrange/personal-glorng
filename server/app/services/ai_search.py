from collections.abc import AsyncIterator
from enum import StrEnum

from app.core.logging import logger
from app.db.models.search_document import SearchVisibility
from app.services.ai_chat import OpenAIService
from app.services.search_index import SearchIndexService

SEARCH_SYSTEM_PROMPT = (
    "You are a personal search assistant for a developer portfolio platform. "
    "Answer only using the numbered context blocks provided below. "
    "Cite sources as [1], [2], etc. matching those numbers. "
    "If the context is empty or does not contain the answer, say: "
    '"I couldn\'t find that in your indexed content." '
    "Do not invent projects, recipes, tasks, expenses, or other facts. "
    "Keep answers concise and technical unless asked otherwise."
)

SEARCH_TEMPERATURE = 0.3


class SearchScope(StrEnum):
    PUBLIC = "public"
    PERSONAL = "personal"


def _visibilities_for_scope(scope: SearchScope) -> list[SearchVisibility]:
    if scope == SearchScope.PUBLIC:
        return [SearchVisibility.PUBLIC]
    return [SearchVisibility.PUBLIC, SearchVisibility.ADMIN]


def _extract_last_user_query(messages: list[dict[str, str]]) -> str:
    for message in reversed(messages):
        if message.get("role") == "user":
            return str(message.get("content", "")).strip()
    return ""


def _build_system_prompt(context_block: str) -> str:
    return f"{SEARCH_SYSTEM_PROMPT}\n\n---\nContext:\n{context_block}"


class AiSearchService:
    """Retrieve-then-generate chat backed by Postgres FTS."""

    def __init__(
        self,
        search_svc: SearchIndexService,
        llm_svc: OpenAIService,
    ) -> None:
        self._search = search_svc
        self._llm = llm_svc

    async def stream_events(
        self,
        messages: list[dict[str, str]],
        *,
        scope: SearchScope,
    ) -> AsyncIterator[dict[str, object]]:
        query = _extract_last_user_query(messages)
        results = await self._search.search(
            query,
            visibilities=_visibilities_for_scope(scope),
        )
        sources = SearchIndexService.to_sources(results)
        context_block = SearchIndexService.build_context_block(results)

        logger.info(
            "AI search retrieval completed",
            context={
                "scope": scope.value,
                "query": query[:120],
                "hits": len(results),
            },
        )

        yield {"sources": sources}

        system_prompt = _build_system_prompt(context_block)
        async for delta in self._llm.stream(
            messages,
            system_prompt=system_prompt,
            temperature=SEARCH_TEMPERATURE,
        ):
            yield {"delta": delta}

        yield {"done": True, "model": self._llm.model}
