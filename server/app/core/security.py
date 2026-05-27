import uuid
from datetime import UTC, datetime, timedelta

import bcrypt
import jwt

from app.settings import get_settings


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def _create_token(
    subject: str,
    token_type: str,
    expires_delta: timedelta,
    *,
    include_jti: bool = True,
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
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def create_access_token(
    subject: str,
    expires_delta: timedelta | None = None,
) -> str:
    settings = get_settings()
    delta = expires_delta or timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    return _create_token(subject, "access", delta)


def create_refresh_token(subject: str) -> str:
    settings = get_settings()
    return _create_token(
        subject, "refresh", timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    )


def create_verification_token(email: str) -> str:
    return _create_token(email, "verify", timedelta(hours=24))


def create_reset_token(email: str) -> str:
    return _create_token(email, "reset", timedelta(hours=1))


def decode_token(token: str) -> dict:
    settings = get_settings()
    try:
        return jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
    except jwt.PyJWTError as e:
        raise ValueError(f"Invalid token: {e}") from e
