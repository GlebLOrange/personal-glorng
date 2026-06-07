"""Shared pagination query parameters."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Annotated

from fastapi import Query

from app.core.utils import paginate_params


@dataclass(frozen=True)
class PaginationParams:
    page: int
    per_page: int
    offset: int
    limit: int


def pagination_params_factory(
    default_per_page: int = 20,
) -> Callable[..., PaginationParams]:
    def _pagination_params(
        page: Annotated[int, Query(ge=1)] = 1,
        per_page: Annotated[int, Query(ge=1, le=100)] = default_per_page,
    ) -> PaginationParams:
        safe_page = max(1, page)
        offset, limit = paginate_params(safe_page, per_page)
        return PaginationParams(
            page=safe_page,
            per_page=limit,
            offset=offset,
            limit=limit,
        )

    return _pagination_params


pagination_params = pagination_params_factory()
audit_pagination_params = pagination_params_factory(50)
