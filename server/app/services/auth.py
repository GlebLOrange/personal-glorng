from datetime import UTC, datetime

from app.core.exceptions import ConflictError, ForbiddenError, UnauthorizedError
from app.core.logging import logger
from app.core.redis import is_token_blacklisted, try_blacklist_token
from app.core.security import (
    create_access_token,
    create_refresh_token,
    create_reset_token,
    decode_token,
    hash_password,
    require_matching_session_version,
    verify_password,
)
from app.db.documents.audit import AuditActorType, AuditCategory, AuditSource
from app.db.documents.user import User
from app.db.registry import DatabaseRegistry
from app.services.audit import AuditRecord, AuditService
from app.services.user import (
    create_user,
    default_user_permissions,
    get_user_by_email,
    get_user_by_public_id,
)
from app.settings import get_settings


def _auth_log_email(email: str) -> str:
    """Redact email in production auth logs."""
    if get_settings().APP_ENV != "production":
        return email
    local, _, domain = email.partition("@")
    if not local:
        return "***"
    return f"{local[0]}***@{domain}" if domain else "***"


async def _decode_and_validate(token: str, expected_type: str) -> dict[str, object]:
    """Decode a JWT and verify its type claim, raising UnauthorizedError on failure."""
    try:
        payload = decode_token(token)
    except ValueError:
        raise UnauthorizedError(
            f"Invalid or expired {expected_type} token",
        ) from None

    if payload.get("type") != expected_type:
        raise UnauthorizedError("Invalid token type")

    if not payload.get("sub"):
        raise UnauthorizedError("Invalid token payload")

    jti = payload.get("jti")
    if jti and await is_token_blacklisted(jti):
        raise UnauthorizedError("Token has already been used")

    return payload


async def _claim_payload(payload: dict[str, object]) -> None:
    """Atomically blacklist a token's JTI; raise if already used."""
    jti = payload.get("jti")
    if not jti:
        return
    exp = payload.get("exp", 0)
    now = int(datetime.now(UTC).timestamp())
    claimed = await try_blacklist_token(str(jti), max(int(exp) - now, 0))
    if not claimed:
        raise UnauthorizedError("Token has already been used")


async def _get_user_by_sub(registry: DatabaseRegistry, subject: str) -> User:
    user = await get_user_by_public_id(registry, subject)
    if not user:
        raise UnauthorizedError("User not found")
    return user


async def register_user(
    registry: DatabaseRegistry,
    audit: AuditService,
    email: str,
    password: str,
    *,
    display_name: str | None = None,
    timezone: str = "UTC",
) -> User:
    normalized_email = email.strip().lower()

    existing = await get_user_by_email(registry, normalized_email)
    if existing:
        raise ConflictError("User with this email already exists")

    user = await create_user(
        registry,
        email=normalized_email,
        password=password,
        permissions=default_user_permissions(),
        is_verified=False,
        display_name=display_name,
        timezone=timezone,
    )

    await audit.record(
        AuditRecord(
            category=AuditCategory.SECURITY,
            action="auth.registered",
            actor_type=AuditActorType.USER,
            actor_id=user.id,
            source=AuditSource.PUBLIC,
            resource_type="user",
            resource_id=user.id,
            metadata={"email": normalized_email},
        ),
    )
    return user


async def login_user(
    registry: DatabaseRegistry,
    audit: AuditService,
    email: str,
    password: str,
) -> tuple[str, str]:
    user = await get_user_by_email(registry, email.strip().lower())
    if not user or not await verify_password(password, user.hashed_password):
        logger.warning("Login failed", context={"email": _auth_log_email(email)})
        await audit.record(
            AuditRecord(
                category=AuditCategory.SECURITY,
                action="auth.login_failed",
                actor_type=AuditActorType.USER,
                source=AuditSource.PUBLIC,
                metadata={"email": email},
            ),
        )
        raise UnauthorizedError("Invalid email or password")

    if not user.is_verified:
        raise ForbiddenError("Email not verified. Check your inbox.")

    access_token = create_access_token(
        str(user.public_id),
        user_id=user.id,
        session_version=user.session_version,
    )
    refresh_token = create_refresh_token(
        str(user.public_id),
        session_version=user.session_version,
    )
    await audit.record(
        AuditRecord(
            category=AuditCategory.SECURITY,
            action="auth.login_success",
            actor_type=AuditActorType.USER,
            actor_id=user.id,
            source=AuditSource.PUBLIC,
            resource_type="user",
            resource_id=user.id,
        ),
    )
    return access_token, refresh_token


async def refresh_access_token(
    registry: DatabaseRegistry,
    audit: AuditService,
    refresh_token: str,
) -> tuple[str, str]:
    payload = await _decode_and_validate(refresh_token, "refresh")
    await _claim_payload(payload)
    user = await _get_user_by_sub(registry, str(payload["sub"]))
    try:
        require_matching_session_version(payload, user.session_version)
    except ValueError:
        raise UnauthorizedError("Token has been revoked") from None
    new_access = create_access_token(
        str(user.public_id),
        user_id=user.id,
        session_version=user.session_version,
    )
    new_refresh = create_refresh_token(
        str(user.public_id),
        session_version=user.session_version,
    )

    await audit.record(
        AuditRecord(
            category=AuditCategory.SECURITY,
            action="auth.token_refreshed",
            actor_type=AuditActorType.USER,
            actor_id=user.id,
            source=AuditSource.PUBLIC,
            resource_type="user",
            resource_id=user.id,
        ),
    )
    return new_access, new_refresh


async def verify_user_email(
    registry: DatabaseRegistry,
    audit: AuditService,
    token: str,
) -> User:
    payload = await _decode_and_validate(token, "verify")
    await _claim_payload(payload)
    user = await get_user_by_email(registry, str(payload["sub"]))
    if not user:
        raise UnauthorizedError("User not found")

    await registry.users.update_fields(user.id, is_verified=True)  # type: ignore[union-attr]
    user = await get_user_by_email(registry, str(payload["sub"]))
    if not user:
        raise UnauthorizedError("User not found")

    await audit.record(
        AuditRecord(
            category=AuditCategory.SECURITY,
            action="auth.email_verified",
            actor_type=AuditActorType.USER,
            actor_id=user.id,
            source=AuditSource.PUBLIC,
            resource_type="user",
            resource_id=user.id,
        ),
    )
    return user


async def request_password_reset(
    registry: DatabaseRegistry,
    audit: AuditService,
    email: str,
) -> str | None:
    user = await get_user_by_email(registry, email.strip().lower())
    if not user:
        return None

    await audit.record(
        AuditRecord(
            category=AuditCategory.SECURITY,
            action="auth.password_reset_requested",
            actor_type=AuditActorType.USER,
            actor_id=user.id,
            source=AuditSource.PUBLIC,
            resource_type="user",
            resource_id=user.id,
            metadata={"email": email},
        ),
    )
    return create_reset_token(email)


async def reset_user_password(
    registry: DatabaseRegistry,
    audit: AuditService,
    token: str,
    new_password: str,
) -> User:
    payload = await _decode_and_validate(token, "reset")
    await _claim_payload(payload)
    user = await get_user_by_email(registry, str(payload["sub"]))
    if not user:
        raise UnauthorizedError("User not found")

    user = await registry.users.update_fields(  # type: ignore[union-attr]
        user.id,
        hashed_password=await hash_password(new_password),
        session_version=int(user.session_version or 0) + 1,
    )

    await audit.record(
        AuditRecord(
            category=AuditCategory.SECURITY,
            action="auth.password_reset_completed",
            actor_type=AuditActorType.USER,
            actor_id=user.id,
            source=AuditSource.PUBLIC,
            resource_type="user",
            resource_id=user.id,
        ),
    )
    return user


async def record_logout(
    audit: AuditService,
    user_id: int | None,
) -> None:
    await audit.record(
        AuditRecord(
            category=AuditCategory.SECURITY,
            action="auth.logout",
            actor_type=AuditActorType.USER,
            actor_id=user_id,
            source=AuditSource.PUBLIC,
            resource_type="user",
            resource_id=user_id,
        ),
    )
