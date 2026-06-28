"""Bounded reads for multipart uploads."""

from fastapi import UploadFile
from starlette.requests import Request

from app.core.exceptions import ApiError

_UPLOAD_CHUNK_SIZE = 64 * 1024


async def read_request_body_bounded(request: Request, max_size: int) -> bytes:
    """Read a raw request body in chunks; reject before exceeding max_size bytes."""
    chunks: list[bytes] = []
    total = 0
    async for chunk in request.stream():
        total += len(chunk)
        if total > max_size:
            raise ApiError(413, f"Request body exceeds {max_size} byte limit")
        chunks.append(chunk)
    return b"".join(chunks)


async def read_upload_bounded(file: UploadFile, max_size: int) -> bytes:
    """Read upload in chunks; reject before exceeding max_size bytes."""
    if file.size is not None and file.size > max_size:
        raise ApiError(413, f"File exceeds {max_size // (1024 * 1024)} MB limit")

    chunks: list[bytes] = []
    total = 0
    while True:
        chunk = await file.read(_UPLOAD_CHUNK_SIZE)
        if not chunk:
            break
        total += len(chunk)
        if total > max_size:
            raise ApiError(413, f"File exceeds {max_size // (1024 * 1024)} MB limit")
        chunks.append(chunk)
    return b"".join(chunks)
