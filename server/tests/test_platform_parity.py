from app.core.permissions import permission_key
from app.platform.registry import PLATFORM_SERVICES


def test_registry_services_have_permission_keys() -> None:
    for service in PLATFORM_SERVICES:
        for capability in service.capabilities:
            key = permission_key(service.slug, capability)
            assert ":" in key
            assert key.startswith(f"{service.slug}:")


def test_registry_slugs_are_unique() -> None:
    slugs = [s.slug for s in PLATFORM_SERVICES]
    assert len(slugs) == len(set(slugs))


def test_registry_api_prefixes_are_unique() -> None:
    prefixes = [s.api_prefix for s in PLATFORM_SERVICES]
    assert len(prefixes) == len(set(prefixes))
