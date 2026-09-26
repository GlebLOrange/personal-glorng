"""QR code records saved by admins (public tool stays ephemeral)."""

from typing import Literal

from pydantic import Field

from app.db.documents.base import TimestampedDocument

QrErrorLevel = Literal["L", "M", "Q", "H"]


class QrCode(TimestampedDocument):
    """Persisted QR payload for capability-gated library routes."""

    content: str = Field(max_length=2000)
    label: str | None = Field(default=None, max_length=120)
    error_level: QrErrorLevel = "M"
    created_by: int
