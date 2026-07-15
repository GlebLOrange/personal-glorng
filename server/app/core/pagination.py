"""Shared pagination query parameters."""

from collections.abc import Callable
from dataclasses import dataclass
from math import ceil
from typing import Annotated, TypeVar

from fastapi import Query

from app.core.utils import DEFAULT_PER_PAGE, paginate_params
from app.schemas.common import PaginatedResponse

T = TypeVar("T")


@dataclass(frozen=True)
class PaginationParams:
    page: int
    per_page: int
    offset: int
    limit: int


def build_paginated[T](
    items: list[T],
    *,
    total: int,
    page: int,
    per_page: int,
) -> PaginatedResponse[T]:
    """Build a paginated API response from a page slice and total count."""
    pages = ceil(total / per_page) if total > 0 else 0
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        per_page=per_page,
        pages=pages,
    )


def pagination_params_factory(
    default_per_page: int = DEFAULT_PER_PAGE,
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
audit_pagination_params = pagination_params_factory()
