import re
import uuid
from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator

from app.core.password_policy import validate_password_strength

_TIMEZONE_ERROR = "Invalid IANA timezone"


def _validate_timezone(value: str) -> str:
    try:
        ZoneInfo(value)
    except ZoneInfoNotFoundError as exc:
        raise ValueError(_TIMEZONE_ERROR) from exc
    return value


def _normalize_email(value: str) -> str:
    return value.strip().lower()


class CredentialsRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return _normalize_email(value)

    @field_validator("password")
    @classmethod
    def check_password(cls, value: str) -> str:
        return validate_password_strength(value)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"email": "admin@glorng.dev", "password": "StrongPass123!"}
        }
    )


LoginRequest = CredentialsRequest


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12)
    password_confirm: str = Field(min_length=12)
    display_name: str | None = Field(default=None, max_length=100)
    timezone: str = "UTC"
    accept_terms: bool = False

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return _normalize_email(value)

    @field_validator("password", "password_confirm")
    @classmethod
    def check_password(cls, value: str) -> str:
        return validate_password_strength(value)

    @field_validator("timezone")
    @classmethod
    def check_timezone(cls, value: str) -> str:
        return _validate_timezone(value)

    @field_validator("display_name")
    @classmethod
    def strip_display_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        trimmed = value.strip()
        return trimmed or None

    @model_validator(mode="after")
    def passwords_match(self) -> "RegisterRequest":
        if self.password != self.password_confirm:
            raise ValueError("Passwords do not match")
        if not self.accept_terms:
            raise ValueError("You must accept the privacy policy")
        return self


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

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return _normalize_email(value)


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=12)
    password_confirm: str = Field(min_length=12)

    @field_validator("new_password", "password_confirm")
    @classmethod
    def check_password(cls, value: str) -> str:
        return validate_password_strength(value)

    @model_validator(mode="after")
    def passwords_match(self) -> "ResetPasswordRequest":
        if self.new_password != self.password_confirm:
            raise ValueError("Passwords do not match")
        return self


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=12)
    password_confirm: str = Field(min_length=12)

    @field_validator("new_password", "password_confirm")
    @classmethod
    def check_password(cls, value: str) -> str:
        return validate_password_strength(value)

    @model_validator(mode="after")
    def passwords_match(self) -> "ChangePasswordRequest":
        if self.new_password != self.password_confirm:
            raise ValueError("Passwords do not match")
        if self.new_password == self.current_password:
            raise ValueError("New password must differ from current password")
        return self


class UpdateProfileRequest(BaseModel):
    display_name: str | None = Field(default=None, max_length=100)
    timezone: str | None = None

    @field_validator("display_name")
    @classmethod
    def strip_display_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        trimmed = value.strip()
        return trimmed or None

    @field_validator("timezone")
    @classmethod
    def check_timezone(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return _validate_timezone(value)


class ChangeEmailRequest(BaseModel):
    email: EmailStr
    current_password: str

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return _normalize_email(value)


class UserPreferencesResponse(BaseModel):
    display_currency: str | None = None


class UpdatePreferencesRequest(BaseModel):
    display_currency: str | None = Field(default=None, max_length=8)

    @field_validator("display_currency")
    @classmethod
    def normalize_currency(cls, value: str | None) -> str | None:
        if value is None:
            return None
        trimmed = value.strip().upper()
        if not trimmed or not re.fullmatch(r"[A-Z]{3}", trimmed):
            raise ValueError("display_currency must be a 3-letter ISO code")
        return trimmed


class DeleteAccountRequest(BaseModel):
    current_password: str
    confirm: bool = False

    @model_validator(mode="after")
    def confirm_delete(self) -> "DeleteAccountRequest":
        if not self.confirm:
            raise ValueError("Account deletion must be confirmed")
        return self


class UserResponse(BaseModel):
    id: uuid.UUID = Field(validation_alias="public_id")
    email: str
    is_verified: bool
    permissions: list[str]
    display_name: str | None = None
    timezone: str = "UTC"
    preferences: dict[str, object] = Field(default_factory=dict)
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "admin@glorng.dev",
                "is_verified": True,
                "permissions": ["platform:superuser"],
                "display_name": "Admin",
                "timezone": "UTC",
                "preferences": {"display_currency": "PLN"},
                "created_at": "2026-05-25T03:00:00Z",
            }
        },
    )
