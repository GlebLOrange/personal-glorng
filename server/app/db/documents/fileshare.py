from datetime import datetime

from app.db.documents.base import TimestampedDocument


class SharedFile(TimestampedDocument):
    code: str
    original_filename: str
    file_path: str
    file_size: int
    content_type: str
    downloads: int = 0
    expires_at: datetime
    created_by: int
