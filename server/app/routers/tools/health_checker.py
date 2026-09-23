"""Website/API health checker tool API."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.core.deps import AuthorizedUser, require_capability
from app.core.permissions import SUPERUSER_PERMISSION, user_has_permission
from app.core.rate_limit import rate_limit_api
from app.core.utils import DEFAULT_PER_PAGE
from app.db.deps import DbRegistry
from app.openapi import requires_capability
from app.schemas.health_checker import (
    HealthHistoryResponse,
    HealthMonitorCreate,
    HealthMonitorListResponse,
    HealthMonitorResponse,
    HealthMonitorUpdate,
)
from app.services.health_checker import HealthMonitorService

router = APIRouter(prefix="/health-checker", tags=["health-checker"])


def _is_superuser(user: object) -> bool:
    return user_has_permission(user, SUPERUSER_PERMISSION)  # type: ignore[arg-type]


@router.get(
    "",
    response_model=HealthMonitorListResponse,
    summary="List health monitors",
    description=requires_capability("health-checker", "read"),
    dependencies=[
        Depends(rate_limit_api),
        Depends(require_capability("health-checker", "read")),
    ],
)
async def list_monitors(
    registry: DbRegistry,
    user: AuthorizedUser,
    page: Annotated[int, Query(ge=1)] = 1,
    per_page: Annotated[int, Query(ge=1, le=100)] = DEFAULT_PER_PAGE,
) -> HealthMonitorListResponse:
    svc = HealthMonitorService(registry)
    return await svc.list_by_owner(created_by=user.id, page=page, per_page=per_page)


@router.post(
    "",
    response_model=HealthMonitorResponse,
    status_code=201,
    summary="Create health monitor",
    description=requires_capability("health-checker", "write"),
    dependencies=[
        Depends(rate_limit_api),
        Depends(require_capability("health-checker", "write")),
    ],
)
async def create_monitor(
    data: HealthMonitorCreate,
    registry: DbRegistry,
    user: AuthorizedUser,
) -> HealthMonitorResponse:
    svc = HealthMonitorService(registry)
    monitor = await svc.create_monitor(
        url=str(data.url),
        created_by=user.id,
        label=data.label,
        interval_minutes=data.interval_minutes,
    )
    return HealthMonitorResponse.model_validate(monitor)


@router.get(
    "/{monitor_id}",
    response_model=HealthMonitorResponse,
    summary="Get health monitor",
    description=requires_capability("health-checker", "read"),
    dependencies=[
        Depends(rate_limit_api),
        Depends(require_capability("health-checker", "read")),
    ],
)
async def get_monitor(
    monitor_id: int,
    registry: DbRegistry,
    user: AuthorizedUser,
) -> HealthMonitorResponse:
    svc = HealthMonitorService(registry)
    monitor = await svc.get_monitor(
        monitor_id,
        actor_id=user.id,
        is_superuser=_is_superuser(user),
    )
    return HealthMonitorResponse.model_validate(monitor)


@router.get(
    "/{monitor_id}/history",
    response_model=HealthHistoryResponse,
    summary="Health check history",
    description=requires_capability("health-checker", "read"),
    dependencies=[
        Depends(rate_limit_api),
        Depends(require_capability("health-checker", "read")),
    ],
)
async def get_history(
    monitor_id: int,
    registry: DbRegistry,
    user: AuthorizedUser,
    hours: Annotated[int, Query(ge=1, le=168)] = 24,
) -> HealthHistoryResponse:
    svc = HealthMonitorService(registry)
    return await svc.get_history(
        monitor_id,
        actor_id=user.id,
        is_superuser=_is_superuser(user),
        hours=hours,
    )


@router.patch(
    "/{monitor_id}",
    response_model=HealthMonitorResponse,
    summary="Update health monitor",
    description=requires_capability("health-checker", "write"),
    dependencies=[
        Depends(rate_limit_api),
        Depends(require_capability("health-checker", "write")),
    ],
)
async def update_monitor(
    monitor_id: int,
    data: HealthMonitorUpdate,
    registry: DbRegistry,
    user: AuthorizedUser,
) -> HealthMonitorResponse:
    svc = HealthMonitorService(registry)
    payload = data.model_dump(exclude_unset=True)
    monitor = await svc.update_monitor(
        monitor_id,
        actor_id=user.id,
        is_superuser=_is_superuser(user),
        fields=payload,
    )
    return HealthMonitorResponse.model_validate(monitor)


@router.post(
    "/{monitor_id}/check",
    response_model=HealthMonitorResponse,
    summary="Run health check now",
    description=requires_capability("health-checker", "write"),
    dependencies=[
        Depends(rate_limit_api),
        Depends(require_capability("health-checker", "write")),
    ],
)
async def check_now(
    monitor_id: int,
    registry: DbRegistry,
    user: AuthorizedUser,
) -> HealthMonitorResponse:
    svc = HealthMonitorService(registry)
    monitor = await svc.check_now(
        monitor_id,
        actor_id=user.id,
        is_superuser=_is_superuser(user),
    )
    return HealthMonitorResponse.model_validate(monitor)


@router.delete(
    "/{monitor_id}",
    status_code=204,
    summary="Delete health monitor",
    description=requires_capability("health-checker", "write"),
    dependencies=[
        Depends(rate_limit_api),
        Depends(require_capability("health-checker", "write")),
    ],
)
async def delete_monitor(
    monitor_id: int,
    registry: DbRegistry,
    user: AuthorizedUser,
) -> None:
    svc = HealthMonitorService(registry)
    await svc.delete_monitor(
        monitor_id,
        actor_id=user.id,
        is_superuser=_is_superuser(user),
    )
