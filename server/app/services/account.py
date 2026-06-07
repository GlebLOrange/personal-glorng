"""Self-service account profile, security, and preferences."""

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, UnauthorizedError
from app.core.logging import logger
from app.core.permissions import SUPERUSER_PERMISSION
from app.core.security import (
    create_verification_token,
    hash_password,
    verify_password,
)
from app.db.models.audit_event import AuditActorType, AuditCategory, AuditSource
from app.db.models.github_credential import GitHubCredential
from app.db.models.user import User
from app.db.models.weather_location import WeatherLocation
from app.services.audit import AuditRecord, AuditService
from app.services.auth import get_user_by_email
from app.services.user import default_display_name, ensure_user_mutable

ALLOWED_PREFERENCE_KEYS = frozenset({"display_currency"})


async def update_profile(
    db: AsyncSession,
    user: User,
    *,
    display_name: str | None = None,
    timezone: str | None = None,
) -> User:
    """Update editable profile fields."""
    if display_name is not None:
        user.display_name = display_name or default_display_name(user.email)
    if timezone is not None:
        user.timezone = timezone

    await db.flush()
    await db.refresh(user)

    audit = AuditService(db)
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
    db: AsyncSession,
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

    existing = await get_user_by_email(db, normalized)
    if existing:
        raise ConflictError("Email is already in use")

    user.email = normalized
    user.is_verified = False
    await db.flush()
    await db.refresh(user)

    audit = AuditService(db)
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
    db: AsyncSession,
    user: User,
    *,
    current_password: str,
    new_password: str,
) -> User:
    """Change password for the authenticated user."""
    if not verify_password(current_password, user.hashed_password):
        raise UnauthorizedError("Current password is incorrect")

    user.hashed_password = hash_password(new_password)
    await db.flush()
    await db.refresh(user)

    audit = AuditService(db)
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
    db: AsyncSession,
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

    user.preferences = current
    await db.flush()
    await db.refresh(user)

    audit = AuditService(db)
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
    return get_preferences(user)


async def delete_account(
    db: AsyncSession,
    user: User,
    *,
    current_password: str,
) -> None:
    """Permanently delete the authenticated user's account."""
    ensure_user_mutable(user)

    if SUPERUSER_PERMISSION in (user.permissions or []):
        result = await db.execute(select(User))
        superuser_count = sum(
            1
            for row in result.scalars().all()
            if SUPERUSER_PERMISSION in (row.permissions or [])
        )
        if superuser_count <= 1:
            raise ConflictError("Cannot delete the last superuser account")

    if not verify_password(current_password, user.hashed_password):
        raise UnauthorizedError("Current password is incorrect")

    user_id = user.id
    await db.execute(delete(WeatherLocation).where(WeatherLocation.user_id == user_id))
    await db.execute(
        delete(GitHubCredential).where(GitHubCredential.user_id == user_id)
    )
    await db.delete(user)
    await db.flush()

    audit = AuditService(db)
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
