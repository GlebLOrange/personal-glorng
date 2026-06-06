from fastapi import APIRouter

from app.core.feature_flags import is_service_enabled
from app.platform.registry import CATEGORY_LABELS, PLATFORM_SERVICES
from app.schemas.platform import PlatformCatalogResponse, PlatformServiceResponse

router = APIRouter(prefix="/platform", tags=["platform"])


@router.get("/services", response_model=PlatformCatalogResponse)
async def list_platform_services() -> PlatformCatalogResponse:
    """Return the platform service catalog for admin UI and tooling."""
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
