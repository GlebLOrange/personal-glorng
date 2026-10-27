import pytest
from httpx import AsyncClient
from pydantic import BaseModel

from app.core.pagination import build_paginated, pagination_params_factory
from app.core.utils import DEFAULT_PER_PAGE
from app.schemas.common import PaginatedResponse


def test_default_per_page_is_twenty_five() -> None:
    assert DEFAULT_PER_PAGE == 25


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


class _Item(BaseModel):
    value: int


class _ItemList(PaginatedResponse[_Item]):
    """Concrete response type, like the per-tool list schemas."""


def test_build_paginated_returns_concrete_response_type() -> None:
    result = build_paginated(
        [_Item(value=1)],
        total=3,
        page=1,
        per_page=2,
        response_cls=_ItemList,
    )

    assert isinstance(result, _ItemList)
    assert result.total == 3
    assert result.pages == 2
    assert [item.value for item in result.items] == [1]


def test_build_paginated_zero_total_has_zero_pages() -> None:
    result = build_paginated(
        [],
        total=0,
        page=1,
        per_page=10,
        response_cls=_ItemList,
    )

    assert result.pages == 0
    assert result.items == []
