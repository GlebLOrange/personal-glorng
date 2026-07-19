from datetime import UTC, datetime

import pytest
from httpx import AsyncClient

from app.db.documents.search import SearchVisibility
from app.db.documents.task import Task, TaskStatus
from app.db.registry import DatabaseRegistry
from app.services.search_index import SearchDocumentInput, SearchIndexService
from app.services.task import TaskService
from tests.env_helpers import ENV_SCENARIOS_DIR, activate_env_file

SEARCH_QUERY_URL = "/api/search"


@pytest.fixture(autouse=True)
def enable_ai_search(monkeypatch: pytest.MonkeyPatch) -> None:
    activate_env_file(monkeypatch, ENV_SCENARIOS_DIR / "ai-search.env")


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
    assert create_resp.status_code == 201

    resp = await client.get(SEARCH_QUERY_URL, params={"q": "Vue"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["query"] == "Vue"
    assert len(body["hits"]) == 1
    assert body["hits"][0]["title"] == "Vue Weeknight Bowl"


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
async def test_search_postgres_mirror_failure_keeps_mongo(
    registry: DatabaseRegistry,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Postgres mirror failures must not fail the request after Mongo upsert."""

    async def fail_upsert_postgres(
        self: SearchIndexService,
        document: SearchDocumentInput,
    ) -> None:
        raise RuntimeError("mirror unavailable")

    class _PostgresEnabledSettings:
        def enable_postgres(self) -> bool:
            return True

    monkeypatch.setattr(SearchIndexService, "_upsert_postgres", fail_upsert_postgres)
    monkeypatch.setattr(
        "app.services.search_index.get_settings",
        lambda: _PostgresEnabledSettings(),
    )

    svc = SearchIndexService(registry, postgres_db=object())  # type: ignore[arg-type]
    saved = await svc.upsert(
        SearchDocumentInput(
            source_type="resume",
            source_id=99,
            title="Mirror Probe",
            body="FastAPI portfolio probe",
            url="/",
            visibility=SearchVisibility.PUBLIC,
        ),
    )

    hits = await svc.search("probe", visibilities=[SearchVisibility.PUBLIC])
    assert saved.title == "Mirror Probe"
    assert len(hits) == 1
    assert hits[0].source_id == 99
