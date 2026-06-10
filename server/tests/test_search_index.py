from collections.abc import AsyncIterator
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import patch

import pytest
from httpx import AsyncClient

from app.core.deps import get_ai_search_service
from app.db.documents.search import SearchVisibility
from app.db.documents.task import Task, TaskStatus
from app.db.registry import DatabaseRegistry
from app.main import app
from app.services.ai_search import AiSearchService
from app.services.search_index import SearchDocumentInput, SearchIndexService
from app.services.task import TaskService
from app.settings import get_settings
from tests.env_helpers import ENV_SCENARIOS_DIR, activate_env_file, scenario_env

SEARCH_CHAT_URL = "/api/search/chat"
SEARCH_QUERY_URL = "/api/search"
SEARCH_CONFIG_URL = "/api/search/config"


@pytest.fixture(autouse=True)
def enable_ai_search(monkeypatch: pytest.MonkeyPatch) -> None:
    activate_env_file(monkeypatch, ENV_SCENARIOS_DIR / "ai-search.env")


async def _mock_stream(*_args: object, **_kwargs: object) -> AsyncIterator[str]:
    for part in ("Found ", "it"):
        yield part


async def _mock_search_events(
    *_args: object,
    **_kwargs: object,
) -> AsyncIterator[dict[str, object]]:
    yield {
        "sources": [
            {
                "id": 1,
                "title": "Test",
                "url": "/",
                "source_type": "resume",
                "snippet": "bio",
            },
        ],
    }
    async for delta in _mock_stream():
        yield {"delta": delta}
    yield {"done": True, "model": "gpt-4.1"}


@pytest.mark.asyncio
async def test_search_index_upsert_and_search(registry: DatabaseRegistry) -> None:
    svc = SearchIndexService(registry)
    await svc.upsert(
        SearchDocumentInput(
            source_type="resume",
            source_id=1,
            title="Gleb.Y Platform",
            body="FastAPI Vue PostgreSQL portfolio",
            url="/",
            visibility=SearchVisibility.PUBLIC,
        ),
    )

    hits = await svc.search("FastAPI", visibilities=[SearchVisibility.PUBLIC])
    assert len(hits) == 1
    assert hits[0].title == "Gleb.Y Platform"


@pytest.mark.asyncio
async def test_search_index_visibility_filter(registry: DatabaseRegistry) -> None:
    svc = SearchIndexService(registry)
    await svc.upsert(
        SearchDocumentInput(
            source_type="task",
            source_id=1,
            title="Private task",
            body="buy milk",
            url="/admin/tools/tasks",
            visibility=SearchVisibility.ADMIN,
        ),
    )

    public_hits = await svc.search("milk", visibilities=[SearchVisibility.PUBLIC])
    admin_hits = await svc.search(
        "milk",
        visibilities=[SearchVisibility.PUBLIC, SearchVisibility.ADMIN],
    )
    assert public_hits == []
    assert len(admin_hits) == 1


@pytest.mark.asyncio
async def test_public_search_query(
    client: AsyncClient,
    auth_client: AsyncClient,
) -> None:
    create_resp = await auth_client.post(
        "/api/tools/recipes",
        json={
            "title": "Vue Weeknight Bowl",
            "ingredients": ["rice", "vegetables"],
            "steps": ["Cook rice", "Stir fry vegetables"],
            "tags": ["quick"],
        },
    )
    assert create_resp.status_code == 200

    resp = await client.get(SEARCH_QUERY_URL, params={"q": "Vue"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["query"] == "Vue"
    assert len(body["hits"]) == 1
    assert body["hits"][0]["title"] == "Vue Weeknight Bowl"


@pytest.mark.asyncio
async def test_public_search_chat_streams_sources(
    client: AsyncClient,
) -> None:
    search_svc = SearchIndexService.__new__(SearchIndexService)
    ai_search = AiSearchService(search_svc, get_settings())
    app.dependency_overrides[get_ai_search_service] = lambda: ai_search

    with patch.object(
        AiSearchService,
        "stream_events",
        side_effect=_mock_search_events,
    ):
        resp = await client.post(
            SEARCH_CHAT_URL,
            json={"messages": [{"role": "user", "content": "What stack?"}]},
        )

    app.dependency_overrides.pop(get_ai_search_service, None)

    assert resp.status_code == 200
    assert '"sources"' in resp.text
    assert '"delta": "Found "' in resp.text
    assert '"done": true' in resp.text


@pytest.mark.asyncio
async def test_search_config_enabled(client: AsyncClient) -> None:
    resp = await client.get(SEARCH_CONFIG_URL)
    assert resp.status_code == 200
    body = resp.json()
    assert body["enabled"] is True
    assert body["configured"] is True


@pytest.mark.asyncio
async def test_search_config_disabled_without_key(
    client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    activate_env_file(monkeypatch, scenario_env(tmp_path, OPENAI_API_KEY=""))
    resp = await client.get(SEARCH_CONFIG_URL)
    assert resp.status_code == 200
    body = resp.json()
    assert body["enabled"] is False
    assert body["configured"] is False


@pytest.mark.asyncio
async def test_task_status_change_reindexes(registry: DatabaseRegistry) -> None:
    task = Task(
        telegram_user_id=1,
        title="Buy groceries",
        scheduled_at=datetime.now(UTC),
        status=TaskStatus.PENDING,
    )
    task = await registry.tasks.insert(task)  # type: ignore[union-attr]
    await TaskService(registry).update_task_status(
        task=task,
        new_status=TaskStatus.COMPLETED,
    )

    hits = await SearchIndexService(registry).search(
        "groceries",
        visibilities=[SearchVisibility.ADMIN],
    )
    assert len(hits) == 1
    assert hits[0].source_type == "task"
    assert hits[0].title == "Buy groceries"
    assert "completed" in hits[0].body.lower()


@pytest.mark.asyncio
async def test_public_search_disabled(
    client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    activate_env_file(monkeypatch, scenario_env(tmp_path, AI_SEARCH_ENABLED="false"))
    resp = await client.post(
        SEARCH_CHAT_URL,
        json={"messages": [{"role": "user", "content": "hello"}]},
    )
    assert resp.status_code == 503
