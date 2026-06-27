"""Self-service account profile, security, and preferences."""

from app.core.exceptions import ConflictError, UnauthorizedError
from app.core.logging import logger
from app.core.permissions import SUPERUSER_PERMISSION
from app.core.security import (
    create_verification_token,
    hash_password,
    verify_password,
)
from app.db.documents.audit import AuditActorType, AuditCategory, AuditSource
from app.db.documents.user import User
from app.db.registry import DatabaseRegistry
from app.services.audit import AuditRecord, AuditService
from app.services.user import (
    default_display_name,
    ensure_user_mutable,
    get_user_by_email,
)

ALLOWED_PREFERENCE_KEYS = frozenset({"display_currency"})


async def update_profile(
    registry: DatabaseRegistry,
    user: User,
    *,
    display_name: str | None = None,
    timezone: str | None = None,
) -> User:
    """Update editable profile fields."""
    fields: dict[str, object] = {}
    if display_name is not None:
        fields["display_name"] = display_name or default_display_name(user.email)
    if timezone is not None:
        fields["timezone"] = timezone

    if fields:
        user = await registry.users.update_fields(user.id, **fields)  # type: ignore[union-attr]

    audit = AuditService(registry)
    await audit.record(
        AuditRecord(
            category=AuditCategory.SECURITY,
            action="account.profile_updated",
            actor_type=AuditActorType.USER,
            actor_id=user.id,
            source=AuditSource.PUBLIC,
            resource_type="user",
            resource_id=user.id,
        ),
    )
    logger.info("Profile updated", context={"user_id": user.id})
    return user


async def change_email(
    registry: DatabaseRegistry,
    user: User,
    *,
    new_email: str,
    current_password: str,
) -> tuple[User, str]:
    """Change email and require re-verification."""
    if not verify_password(current_password, user.hashed_password):
        raise UnauthorizedError("Current password is incorrect")

    normalized = new_email.strip().lower()
    if normalized == user.email:
        return user, create_verification_token(normalized)

    existing = await get_user_by_email(registry, normalized)
    if existing:
        raise ConflictError("Email is already in use")

    user = await registry.users.update_fields(  # type: ignore[union-attr]
        user.id,
        email=normalized,
        is_verified=False,
    )

    audit = AuditService(registry)
    await audit.record(
        AuditRecord(
            category=AuditCategory.SECURITY,
            action="account.email_changed",
            actor_type=AuditActorType.USER,
            actor_id=user.id,
            source=AuditSource.PUBLIC,
            resource_type="user",
            resource_id=user.id,
            metadata={"email": normalized},
        ),
    )
    logger.info("Email changed", context={"user_id": user.id, "email": normalized})
    return user, create_verification_token(normalized)


async def change_password(
    registry: DatabaseRegistry,
    user: User,
    *,
    current_password: str,
    new_password: str,
) -> User:
    """Change password for the authenticated user."""
    if not verify_password(current_password, user.hashed_password):
        raise UnauthorizedError("Current password is incorrect")

    user = await registry.users.update_fields(  # type: ignore[union-attr]
        user.id,
        hashed_password=hash_password(new_password),
    )

    audit = AuditService(registry)
    await audit.record(
        AuditRecord(
            category=AuditCategory.SECURITY,
            action="account.password_changed",
            actor_type=AuditActorType.USER,
            actor_id=user.id,
            source=AuditSource.PUBLIC,
            resource_type="user",
            resource_id=user.id,
        ),
    )
    logger.info("Password changed", context={"user_id": user.id})
    return user


def get_preferences(user: User) -> dict[str, object]:
    """Return whitelisted preference keys."""
    raw = user.preferences or {}
    return {key: raw[key] for key in ALLOWED_PREFERENCE_KEYS if key in raw}


async def update_preferences(
    registry: DatabaseRegistry,
    user: User,
    updates: dict[str, object],
) -> dict[str, object]:
    """Merge whitelisted preference keys."""
    current = dict(user.preferences or {})
    for key, value in updates.items():
        if key not in ALLOWED_PREFERENCE_KEYS:
            continue
        if value is None:
            current.pop(key, None)
        else:
            current[key] = value

    await registry.users.update_fields(user.id, preferences=current)  # type: ignore[union-attr]

    audit = AuditService(registry)
    await audit.record(
        AuditRecord(
            category=AuditCategory.SECURITY,
            action="account.preferences_updated",
            actor_type=AuditActorType.USER,
            actor_id=user.id,
            source=AuditSource.PUBLIC,
            resource_type="user",
            resource_id=user.id,
            metadata={"keys": list(updates.keys())},
        ),
    )
    logger.info("Preferences updated", context={"user_id": user.id})
    return {key: current[key] for key in ALLOWED_PREFERENCE_KEYS if key in current}


async def delete_account(
    registry: DatabaseRegistry,
    user: User,
    *,
    current_password: str,
) -> None:
    """Permanently delete the authenticated user's account."""
    ensure_user_mutable(user)

    if SUPERUSER_PERMISSION in (user.permissions or []):
        superuser_count = await registry.users.count_superusers(SUPERUSER_PERMISSION)  # type: ignore[union-attr]
        if superuser_count <= 1:
            raise ConflictError("Cannot delete the last superuser account")

    if not verify_password(current_password, user.hashed_password):
        raise UnauthorizedError("Current password is incorrect")

    user_id = user.id
    if registry.weather is not None:
        locations = await registry.weather.list_for_user(user_id)
        for location in locations:
            await registry.weather.delete(location.id)
    if registry.credentials is not None:
        await registry.credentials.delete_github_for_user(user_id)
    await registry.users.delete(user_id)  # type: ignore[union-attr]

    audit = AuditService(registry)
    await audit.record(
        AuditRecord(
            category=AuditCategory.SECURITY,
            action="account.deleted",
            actor_type=AuditActorType.USER,
            actor_id=user_id,
            source=AuditSource.PUBLIC,
            resource_type="user",
            resource_id=user_id,
        ),
    )
    logger.info("Account deleted", context={"user_id": user_id})
