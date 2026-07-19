import uuid
from typing import Any

from pydantic import Field

from app.db.documents.base import TimestampedDocument


class User(TimestampedDocument):
    public_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    email: str
    hashed_password: str
    is_verified: bool = False
    is_protected: bool = False
    permissions: list[str] = Field(default_factory=list)
    display_name: str | None = None
    timezone: str = "UTC"
    preferences: dict[str, Any] = Field(default_factory=dict)
    # Bumped on password/email security events; must match JWT ``sv`` claim.
    session_version: int = 0
