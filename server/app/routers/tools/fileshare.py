from fastapi import APIRouter, Depends, UploadFile
from fastapi.responses import StreamingResponse

from app.core.deps import AdminUser, DbSession, require_admin
from app.core.exceptions import ApiError
from app.core.logging import logger
from app.core.rate_limit import rate_limit_api
from app.core.utils import iter_file, paginate_params
from app.schemas.common import MessageResponse
from app.schemas.fileshare import SharedFileResponse
from app.services import fileshare as fileshare_svc

router = APIRouter(
    prefix="/file-share",
    dependencies=[Depends(require_admin), Depends(rate_limit_api)],
)


@router.post("", response_model=SharedFileResponse)
async def upload_file(
    file: UploadFile,
    db: DbSession,
    user: AdminUser,
) -> SharedFileResponse:
    if not file.filename:
        raise ApiError(400, "No file provided")

    contents = await file.read()
    shared = await fileshare_svc.upload(
        db,
        filename=file.filename,
        contents=contents,
        content_type=file.content_type or "application/octet-stream",
        user_id=user.id,
    )
    logger.info(
        "File uploaded",
        context={"code": shared.code, "filename": file.filename, "size": len(contents)},
    )
    return SharedFileResponse.model_validate(shared)


@router.get("", response_model=list[SharedFileResponse])
async def list_files(
    db: DbSession,
    user: AdminUser,  # noqa: ARG001
    page: int = 1,
    per_page: int = 20,
) -> list[SharedFileResponse]:
    offset, limit = paginate_params(page, per_page)
    files = await fileshare_svc.list_files(db, offset=offset, limit=limit)
    return [SharedFileResponse.model_validate(f) for f in files]


@router.delete("/{file_id}", response_model=MessageResponse)
async def delete_file(
    file_id: int,
    db: DbSession,
    user: AdminUser,  # noqa: ARG001
) -> MessageResponse:
    await fileshare_svc.delete(db, file_id=file_id)
    logger.info("File deleted", context={"file_id": file_id})
    return MessageResponse(message="File deleted")


# --- Public download route (no auth) ---

download_router = APIRouter()


@download_router.get(
    "/f/{code}",
    include_in_schema=False,
    dependencies=[Depends(rate_limit_api)],
)
async def download_shared_file(code: str, db: DbSession) -> StreamingResponse:
    shared, disk_path = await fileshare_svc.get_by_code(db, code=code)

    return StreamingResponse(
        iter_file(disk_path),
        media_type=shared.content_type,
        headers={
            "Content-Disposition": f'attachment; filename="{shared.original_filename}"',
            "Content-Length": str(shared.file_size),
        },
    )
