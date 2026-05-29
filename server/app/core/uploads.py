"""Bounded reads for multipart uploads."""

from fastapi import UploadFile

from app.core.exceptions import ApiError

_UPLOAD_CHUNK_SIZE = 64 * 1024


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
