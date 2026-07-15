from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.common import PaginatedResponse


class SharedFileResponse(BaseModel):
    id: int
    code: str
    original_filename: str
    file_size: int
    content_type: str
    downloads: int
    expires_at: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SharedFileListResponse(PaginatedResponse[SharedFileResponse]):
    """Paginated shared file list."""
