"""Permission checks aligned with platform service registry."""

from app.db.documents.user import User
from app.platform.registry import PLATFORM_SERVICES

SUPERUSER_PERMISSION = "platform:superuser"


def permission_key(slug: str, capability: str) -> str:
    """Build a canonical permission string."""
    return f"{slug}:{capability}"


def all_registry_permissions() -> frozenset[str]:
    """All valid slug:capability keys from the platform catalog."""
    keys: set[str] = set()
    for service in PLATFORM_SERVICES:
        for cap in service.capabilities:
            keys.add(permission_key(service.slug, cap))
    return frozenset(keys)


def validate_permissions(permissions: list[str]) -> list[str]:
    """Reject unknown permission strings."""
    if SUPERUSER_PERMISSION in permissions:
        return list(dict.fromkeys(permissions))
    valid = all_registry_permissions()
    unknown = [p for p in permissions if p not in valid]
    if unknown:
        msg = f"Unknown permissions: {', '.join(unknown)}"
        raise ValueError(msg)
    return list(dict.fromkeys(permissions))


def user_has_permission(user: User, key: str) -> bool:
    """Return whether the user may perform the given action."""
    perms = user.permissions or []
    if SUPERUSER_PERMISSION in perms:
        return True
    return key in perms
