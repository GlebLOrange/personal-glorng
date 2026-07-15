import pytest
from httpx import AsyncClient

from app.core.pagination import pagination_params_factory
from app.core.utils import DEFAULT_PER_PAGE


def test_default_per_page_is_nine() -> None:
    assert DEFAULT_PER_PAGE == 9


def test_pagination_params_clamps_per_page() -> None:
    params = pagination_params_factory()(page=2, per_page=500)
    assert params.page == 2
    assert params.per_page == 100
    assert params.offset == 100
    assert params.limit == 100


@pytest.mark.asyncio
async def test_audit_rejects_invalid_per_page(auth_client: AsyncClient) -> None:
    resp = await auth_client.get("/api/tools/audit", params={"per_page": 0})
    assert resp.status_code == 422
