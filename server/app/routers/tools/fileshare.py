"""Temporary file sharing. Default: `file-share:read`; writes: `file-share:write`."""

from fastapi import APIRouter, Depends, Path, UploadFile
from fastapi.responses import StreamingResponse

from app.core.deps import AuthorizedUser, require_capability
from app.core.exceptions import ApiError
from app.core.rate_limit import rate_limit_api
from app.core.uploads import read_upload_bounded
from app.core.utils import DEFAULT_PER_PAGE, attachment_content_disposition, iter_file
from app.db.deps import DbRegistry
from app.openapi import requires_capability
from app.schemas.common import MessageResponse
from app.schemas.fileshare import SharedFileListResponse, SharedFileResponse
from app.services import fileshare as fileshare_svc

router = APIRouter(
    prefix="/file-share",
    tags=["file-share"],
    dependencies=[
        Depends(require_capability("file-share", "read")),
        Depends(rate_limit_api),
    ],
)


@router.post(
    "",
    response_model=SharedFileResponse,
    summary="Upload shared file",
    description=requires_capability("file-share", "write"),
    dependencies=[Depends(require_capability("file-share", "write"))],
)
async def upload_file(
    file: UploadFile,
    registry: DbRegistry,
    user: AuthorizedUser,
) -> SharedFileResponse:
    if not file.filename:
        raise ApiError(400, "No file provided")

    contents = await read_upload_bounded(file, fileshare_svc.MAX_UPLOAD_SIZE)
    shared = await fileshare_svc.upload(
        registry,
        filename=file.filename,
        contents=contents,
        user_id=user.id,
    )
    return SharedFileResponse.model_validate(shared)


@router.get(
    "",
    response_model=SharedFileListResponse,
    summary="List shared files",
    description=requires_capability("file-share", "read"),
)
async def list_files(
    registry: DbRegistry,
    user: AuthorizedUser,
    page: int = 1,
    per_page: int = DEFAULT_PER_PAGE,
) -> SharedFileListResponse:
    return await fileshare_svc.list_files(
        registry,
        page=page,
        per_page=per_page,
        user_id=user.id,
    )


@router.delete(
    "/{file_id}",
    response_model=MessageResponse,
    summary="Delete shared file",
    description=requires_capability("file-share", "write"),
    dependencies=[Depends(require_capability("file-share", "write"))],
)
async def delete_file(
    file_id: int,
    registry: DbRegistry,
    user: AuthorizedUser,
) -> MessageResponse:
    await fileshare_svc.delete(registry, file_id=file_id, user_id=user.id)
    return MessageResponse(message="File deleted")


download_router = APIRouter()


@download_router.get(
    "/f/{code}",
    include_in_schema=False,
    dependencies=[Depends(rate_limit_api)],
)
async def download_shared_file(
    registry: DbRegistry,
    code: str = Path(min_length=1, max_length=16, pattern=r"^[a-zA-Z0-9]+$"),
) -> StreamingResponse:
    shared, disk_path = await fileshare_svc.get_by_code(registry, code=code)

    return StreamingResponse(
        iter_file(disk_path),
        media_type=fileshare_svc.download_media_type(shared.content_type),
        headers={
            "Content-Disposition": attachment_content_disposition(
                shared.original_filename
            ),
            "Content-Length": str(shared.file_size),
        },
    )
