import json
import secrets
from dataclasses import dataclass
from typing import Any

import firebase_admin
from firebase_admin import auth as firebase_auth
from firebase_admin import credentials

from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.security import create_access_token, create_refresh_token
from app.db.documents.audit import AuditActorType, AuditCategory, AuditSource
from app.db.documents.user import User
from app.db.registry import DatabaseRegistry
from app.services.audit import AuditRecord, AuditService
from app.services.user import create_user, get_user_by_email
from app.settings import Settings


@dataclass(frozen=True)
class FirebaseIdentity:
    email: str
    display_name: str | None


@dataclass(frozen=True)
class FirebaseLoginResult:
    user: User
    access_token: str
    refresh_token: str
    created: bool


def _firebase_app(settings: Settings) -> firebase_admin.App:
    app_name = f"glorng-{settings.FIREBASE_PROJECT_ID.strip()}"
    try:
        return firebase_admin.get_app(app_name)
    except ValueError:
        pass

    if settings.FIREBASE_SERVICE_ACCOUNT_JSON.strip():
        service_account = json.loads(settings.FIREBASE_SERVICE_ACCOUNT_JSON)
        cred = credentials.Certificate(service_account)
    else:
        cred = credentials.ApplicationDefault()

    options = {"projectId": settings.FIREBASE_PROJECT_ID}
    return firebase_admin.initialize_app(cred, options, name=app_name)


def verify_firebase_google_token(id_token: str, settings: Settings) -> FirebaseIdentity:
    if not settings.FIREBASE_AUTH_ENABLED:
        raise ForbiddenError("Firebase authentication is disabled")
    if not settings.FIREBASE_PROJECT_ID.strip():
        raise ForbiddenError("Firebase project is not configured")

    try:
        decoded: dict[str, Any] = firebase_auth.verify_id_token(
            id_token,
            app=_firebase_app(settings),
        )
    except Exception as exc:
        raise UnauthorizedError("Invalid Firebase token") from exc

    firebase_claims = decoded.get("firebase")
    provider = (
        firebase_claims.get("sign_in_provider")
        if isinstance(firebase_claims, dict)
        else None
    )
    if provider != "google.com":
        raise UnauthorizedError("Google sign-in is required")

    if decoded.get("email_verified") is not True:
        raise UnauthorizedError("Google email is not verified")

    email = str(decoded.get("email") or "").strip().lower()
    if not email or "@" not in email:
        raise UnauthorizedError("Firebase token is missing an email")

    display_name = str(decoded.get("name") or "").strip() or None
    return FirebaseIdentity(email=email, display_name=display_name)


async def login_with_firebase_google(
    registry: DatabaseRegistry,
    audit: AuditService,
    identity: FirebaseIdentity,
) -> FirebaseLoginResult:
    user = await get_user_by_email(registry, identity.email)
    created = False

    if user is None:
        user = await create_user(
            registry,
            email=identity.email,
            password=secrets.token_urlsafe(48),
            permissions=[],
            is_verified=True,
            display_name=identity.display_name,
        )
        created = True
        await audit.record(
            AuditRecord(
                category=AuditCategory.SECURITY,
                action="auth.firebase_registered",
                actor_type=AuditActorType.USER,
                actor_id=user.id,
                source=AuditSource.PUBLIC,
                resource_type="user",
                resource_id=user.id,
                metadata={"email": identity.email},
            ),
        )
    elif not user.is_verified:
        user = await registry.users.update_fields(user.id, is_verified=True)  # type: ignore[union-attr]

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
            action="auth.firebase_login_success",
            actor_type=AuditActorType.USER,
            actor_id=user.id,
            source=AuditSource.PUBLIC,
            resource_type="user",
            resource_id=user.id,
        ),
    )

    return FirebaseLoginResult(
        user=user,
        access_token=access_token,
        refresh_token=refresh_token,
        created=created,
    )
