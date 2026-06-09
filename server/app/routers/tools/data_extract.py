"""Extract structured data from uploaded CSV, JSON, or XML files."""

from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query, UploadFile

from app.core.deps import require_capability
from app.core.exceptions import ApiError
from app.core.rate_limit import rate_limit_api
from app.core.uploads import read_upload_bounded
from app.openapi import requires_capability
from app.schemas.data_extract import ExtractionResultResponse
from app.services import data_extract as data_extract_svc

router = APIRouter(
    prefix="/data-extract",
    tags=["data-extract"],
    dependencies=[
        Depends(require_capability("data-extract", "read")),
        Depends(rate_limit_api),
    ],
)


@router.post(
    "",
    response_model=ExtractionResultResponse,
    summary="Extract data from uploaded file",
    description=requires_capability("data-extract", "read"),
)
async def extract_file(
    file: UploadFile,
    format: Annotated[
        Literal["csv", "json", "xml"] | None,
        Query(description="Optional format override"),
    ] = None,
    row_tag: Annotated[
        str | None,
        Query(description="Repeated XML element tag for row extraction"),
    ] = None,
    xml_mode: Annotated[
        Literal["rows", "tree"] | None,
        Query(description="XML extraction mode"),
    ] = None,
) -> ExtractionResultResponse:
    if not file.filename:
        raise ApiError(400, "No file provided")

    contents = await read_upload_bounded(file, data_extract_svc.MAX_EXTRACT_SIZE)
    result = data_extract_svc.extract_upload(
        contents,
        filename=file.filename,
        format=format,
        row_tag=row_tag,
        xml_mode=xml_mode,
    )
    return ExtractionResultResponse(
        format=result.format.value,
        records=result.records,
        meta=result.meta,
    )
