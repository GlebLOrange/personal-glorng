import uuid
from datetime import UTC, datetime, timedelta

import bcrypt
import jwt

from app.settings import get_settings


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12)).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def _create_token(
    subject: str,
    token_type: str,
    expires_delta: timedelta,
    *,
    include_jti: bool = True,
    session_version: int | None = None,
    extra: dict | None = None,
) -> str:
    settings = get_settings()
    now = datetime.now(UTC)
    payload: dict = {
        "sub": subject,
        "exp": now + expires_delta,
        "iat": now,
        "type": token_type,
    }
    if include_jti:
        payload["jti"] = str(uuid.uuid4())
    if session_version is not None:
        payload["sv"] = int(session_version)
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def create_access_token(
    subject: str,
    expires_delta: timedelta | None = None,
    *,
    user_id: int | None = None,
    session_version: int = 0,
) -> str:
    settings = get_settings()
    delta = expires_delta or timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    extra: dict = {}
    if user_id is not None:
        extra["uid"] = user_id
    return _create_token(
        subject,
        "access",
        delta,
        session_version=session_version,
        extra=extra or None,
    )


def user_id_from_access_token(raw: str) -> int | None:
    """Return the authenticated user's DB id from an access token, if present."""
    try:
        payload = decode_token(raw)
    except ValueError:
        return None
    if payload.get("type") != "access":
        return None
    uid = payload.get("uid")
    if uid is not None:
        try:
            return int(uid)
        except (ValueError, TypeError):
            return None
    sub = payload.get("sub")
    if sub is None:
        return None
    try:
        return int(sub)
    except (ValueError, TypeError):
        return None


def access_token_from_request(request: object) -> str | None:
    """Extract a bearer or cookie access token from a Starlette request."""
    headers = getattr(request, "headers", None)
    cookies = getattr(request, "cookies", None)
    if headers is not None:
        auth = headers.get("authorization", "")
        if auth.lower().startswith("bearer "):
            token = auth[7:].strip()
            if token:
                return token
    if cookies is not None:
        cookie_token = cookies.get("access_token")
        if cookie_token:
            return cookie_token
    return None


def create_refresh_token(subject: str, *, session_version: int = 0) -> str:
    settings = get_settings()
    return _create_token(
        subject,
        "refresh",
        timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
        session_version=session_version,
    )


def create_verification_token(email: str) -> str:
    return _create_token(email, "verify", timedelta(hours=24))


def create_reset_token(email: str) -> str:
    return _create_token(email, "reset", timedelta(hours=1))


def create_oauth_state_token(
    subject: str,
    expires_delta: timedelta | None = None,
) -> str:
    delta = expires_delta or timedelta(minutes=10)
    return _create_token(
        subject,
        "oauth_state",
        delta,
        include_jti=False,
    )


def decode_token(token: str) -> dict:
    settings = get_settings()
    try:
        return jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
    except jwt.PyJWTError as e:
        raise ValueError(f"Invalid token: {e}") from e


def require_matching_session_version(
    payload: dict,
    session_version: int,
) -> None:
    """Fail closed if JWT ``sv`` is missing or does not match the user."""
    if "sv" not in payload:
        raise ValueError("Token missing session version")
    try:
        token_sv = int(payload["sv"])
    except (TypeError, ValueError) as e:
        raise ValueError("Invalid session version") from e
    if token_sv != int(session_version):
        raise ValueError("Session has been revoked")
