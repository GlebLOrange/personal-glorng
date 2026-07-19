"""Admin search API over indexed admin content."""

import pytest
from httpx import AsyncClient

from app.core.security import create_access_token
from app.db.documents.search import SearchVisibility
from app.db.registry import DatabaseRegistry
from app.services.search_index import SearchDocumentInput, SearchIndexService
from tests.factories import create_user

ADMIN_SEARCH_URL = "/api/tools/search"


@pytest.fixture
async def no_perms_client(
    client: AsyncClient,
    registry: DatabaseRegistry,
):
    user = await create_user(
        registry,
        email="noperms-search@glorng.dev",
        permissions=[],
    )
    token = create_access_token(str(user.public_id), user_id=user.id)
    client.headers["Authorization"] = f"Bearer {token}"
    try:
        yield client
    finally:
        client.headers.pop("Authorization", None)


@pytest.mark.asyncio
async def test_admin_search_returns_admin_hits(
    auth_client: AsyncClient,
    registry: DatabaseRegistry,
) -> None:
    svc = SearchIndexService(registry)
    await svc.upsert(
        SearchDocumentInput(
            source_type="feedback",
            source_id=1,
            title="Feedback: Dark mode",
            body="Please add a dark mode toggle",
            url="/admin/tools/feedback",
            visibility=SearchVisibility.ADMIN,
        ),
    )

    resp = await auth_client.get(ADMIN_SEARCH_URL, params={"q": "dark mode"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["query"] == "dark mode"
    assert len(body["hits"]) == 1
    assert body["hits"][0]["source_type"] == "feedback"


@pytest.mark.asyncio
async def test_admin_search_filters_by_source_type(
    auth_client: AsyncClient,
    registry: DatabaseRegistry,
) -> None:
    svc = SearchIndexService(registry)
    await svc.upsert(
        SearchDocumentInput(
            source_type="task",
            source_id=1,
            title="Buy milk",
            body="groceries",
            url="/admin/tools/tasks",
            visibility=SearchVisibility.ADMIN,
        ),
    )
    await svc.upsert(
        SearchDocumentInput(
            source_type="feedback",
            source_id=2,
            title="Feedback: milk",
            body="allergy note",
            url="/admin/tools/feedback",
            visibility=SearchVisibility.ADMIN,
        ),
    )

    resp = await auth_client.get(
        ADMIN_SEARCH_URL,
        params={"q": "milk", "source_type": "task"},
    )
    assert resp.status_code == 200
    hits = resp.json()["hits"]
    assert len(hits) == 1
    assert hits[0]["source_type"] == "task"


@pytest.mark.asyncio
async def test_admin_search_requires_capability(
    no_perms_client: AsyncClient,
) -> None:
    resp = await no_perms_client.get(ADMIN_SEARCH_URL, params={"q": "test"})
    assert resp.status_code == 403
