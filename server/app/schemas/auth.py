import re
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

PASSWORD_PATTERN = re.compile(r"^(?=.*[a-zA-Z])(?=.*\d).{8,}$")


def _validate_password_strength(v: str) -> str:
    if not PASSWORD_PATTERN.match(v):
        msg = "Password must be 8+ chars with a letter and digit"
        raise ValueError(msg)
    return v


class CredentialsRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)

    _check_password = field_validator("password")(_validate_password_strength)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"email": "admin@glorng.dev", "password": "Strong1234"}
        }
    )


LoginRequest = CredentialsRequest
RegisterRequest = CredentialsRequest


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"  # noqa: S105


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str | None = None


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=8)

    _check_password = field_validator("new_password")(_validate_password_strength)


class UserResponse(BaseModel):
    id: int
    email: str
    is_verified: bool
    is_admin: bool
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "email": "admin@glorng.dev",
                "is_verified": True,
                "is_admin": True,
                "created_at": "2026-05-25T03:00:00Z",
            }
        },
    )
