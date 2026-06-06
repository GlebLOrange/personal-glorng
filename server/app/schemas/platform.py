from pydantic import BaseModel


class PlatformServiceResponse(BaseModel):
    slug: str
    name: str
    category: str
    category_label: str
    description: str
    api_prefix: str
    admin_route: str
    icon: str
    capabilities: list[str]
    external: bool
    public: bool = False


class PlatformCatalogResponse(BaseModel):
    services: list[PlatformServiceResponse]
    categories: dict[str, str]
