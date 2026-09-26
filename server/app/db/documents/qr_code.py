"""QR code records created by the public generator tool."""

from typing import Literal

from pydantic import Field

from app.db.documents.base import TimestampedDocument

QrErrorLevel = Literal["L", "M", "Q", "H"]


class QrCode(TimestampedDocument):
    """Persisted QR payload and rendering options."""

    content: str = Field(max_length=2000)
    label: str | None = Field(default=None, max_length=120)
    error_level: QrErrorLevel = "M"
    created_by: int | None = None
