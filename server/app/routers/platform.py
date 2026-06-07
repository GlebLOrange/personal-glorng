from fastapi import APIRouter

from app.core.feature_flags import is_service_enabled
from app.platform.registry import CATEGORY_LABELS, PLATFORM_SERVICES
from app.schemas.platform import PlatformCatalogResponse, PlatformServiceResponse

router = APIRouter(prefix="/platform", tags=["platform"])


async def _platform_catalog() -> PlatformCatalogResponse:
    services = [
        PlatformServiceResponse(
            slug=s.slug,
            name=s.name,
            category=s.category,
            category_label=CATEGORY_LABELS.get(s.category, s.category.title()),
            description=s.description,
            api_prefix=s.api_prefix,
            admin_route=s.admin_route,
            icon=s.icon,
            capabilities=list(s.capabilities),
            external=s.external,
            public=s.public,
        )
        for s in PLATFORM_SERVICES
        if is_service_enabled(s.slug)
    ]
    return PlatformCatalogResponse(services=services, categories=CATEGORY_LABELS)


@router.get(
    "/services",
    response_model=PlatformCatalogResponse,
    summary="List platform services",
    description="Return the admin service catalog with capabilities and routes.",
)
async def list_platform_services() -> PlatformCatalogResponse:
    return await _platform_catalog()


@router.get(
    "/catalog",
    response_model=PlatformCatalogResponse,
    summary="Platform catalog",
    description="Alias for /platform/services.",
)
async def platform_catalog() -> PlatformCatalogResponse:
    return await _platform_catalog()
