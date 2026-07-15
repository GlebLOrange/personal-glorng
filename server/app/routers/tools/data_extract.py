"""Extract structured data from uploaded CSV, JSON, XML, or delimited files."""

import asyncio
import json
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Path, Query, UploadFile

from app.core.data_extractor.types import ExtractOptions
from app.core.deps import AuthorizedUser, require_capability
from app.core.exceptions import ApiError, ValidationError
from app.core.pagination import build_paginated, paginate_params
from app.core.rate_limit import rate_limit_api
from app.core.uploads import read_upload_bounded
from app.core.utils import DEFAULT_PER_PAGE
from app.db.deps import DbRegistry
from app.openapi import requires_capability
from app.schemas.data_extract import (
    ExtractionResultResponse,
    ImportBatchDetailResponse,
    ImportBatchListResponse,
    ImportBatchResponse,
    ImportResultResponse,
    ImportRowErrorResponse,
    ImportRowResponse,
    PromoteBatchResponse,
)
from app.services import data_extract as data_extract_svc
from app.services import data_import as data_import_svc

router = APIRouter(
    prefix="/data-extract",
    tags=["data-extract"],
    dependencies=[
        Depends(require_capability("data-extract", "read")),
        Depends(rate_limit_api),
    ],
)


def _parse_field_names(raw: str | None) -> list[str] | None:
    if not raw or not raw.strip():
        return None
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValidationError("field_names must be a JSON array of strings") from exc
    if not isinstance(parsed, list) or not all(
        isinstance(item, str) for item in parsed
    ):
        raise ValidationError("field_names must be a JSON array of strings")
    return parsed


def _build_options(
    *,
    profile: str | None,
    row_tag: str | None,
    xml_mode: Literal["rows", "tree"] | None,
    field_delimiter: str | None,
    list_delimiter: str | None,
    field_names: str | None,
) -> ExtractOptions:
    return data_extract_svc.build_extract_options(
        profile=profile,
        row_tag=row_tag,
        xml_mode=xml_mode,
        field_delimiter=field_delimiter,
        list_delimiter=list_delimiter,
        field_names=_parse_field_names(field_names),
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
        Literal["csv", "json", "xml", "delimited"] | None,
        Query(description="Optional format override"),
    ] = None,
    profile: Annotated[
        str | None,
        Query(description="Named extraction profile (e.g. pipe_embed)"),
    ] = None,
    row_tag: Annotated[
        str | None,
        Query(description="Repeated XML element tag for row extraction"),
    ] = None,
    xml_mode: Annotated[
        Literal["rows", "tree"] | None,
        Query(description="XML extraction mode"),
    ] = None,
    field_delimiter: Annotated[
        str | None,
        Query(description="Field delimiter for delimited format"),
    ] = None,
    list_delimiter: Annotated[
        str | None,
        Query(description="List delimiter inside delimited fields"),
    ] = None,
    field_names: Annotated[
        str | None,
        Query(description="JSON array of field names for delimited rows"),
    ] = None,
) -> ExtractionResultResponse:
    if not file.filename:
        raise ApiError(400, "No file provided")

    contents = await read_upload_bounded(file, data_extract_svc.MAX_EXTRACT_SIZE)
    options = _build_options(
        profile=profile,
        row_tag=row_tag,
        xml_mode=xml_mode,
        field_delimiter=field_delimiter,
        list_delimiter=list_delimiter,
        field_names=field_names,
    )
    result = await asyncio.to_thread(
        data_extract_svc.extract_upload,
        contents,
        filename=file.filename,
        format=format,
        options=options,
    )
    return ExtractionResultResponse(
        format=result.format.value,
        records=result.records,
        meta=result.meta,
    )


@router.post(
    "/import",
    response_model=ImportResultResponse,
    summary="Import uploaded file into staging storage",
    description=requires_capability("data-extract", "write"),
    dependencies=[Depends(require_capability("data-extract", "write"))],
)
async def import_file(
    file: UploadFile,
    registry: DbRegistry,
    user: AuthorizedUser,
    format: Annotated[
        Literal["csv", "json", "xml", "delimited"] | None,
        Query(description="Optional format override"),
    ] = None,
    profile: Annotated[
        str | None,
        Query(description="Named extraction profile (e.g. pipe_embed)"),
    ] = None,
    row_tag: Annotated[
        str | None,
        Query(description="Repeated XML element tag for row extraction"),
    ] = None,
    xml_mode: Annotated[
        Literal["rows", "tree"] | None,
        Query(description="XML extraction mode"),
    ] = None,
    field_delimiter: Annotated[
        str | None,
        Query(description="Field delimiter for delimited format"),
    ] = None,
    list_delimiter: Annotated[
        str | None,
        Query(description="List delimiter inside delimited fields"),
    ] = None,
    field_names: Annotated[
        str | None,
        Query(description="JSON array of field names for delimited rows"),
    ] = None,
) -> ImportResultResponse:
    if not file.filename:
        raise ApiError(400, "No file provided")

    contents = await read_upload_bounded(file, data_extract_svc.MAX_EXTRACT_SIZE)
    options = _build_options(
        profile=profile,
        row_tag=row_tag,
        xml_mode=xml_mode,
        field_delimiter=field_delimiter,
        list_delimiter=list_delimiter,
        field_names=field_names,
    )
    result = await data_import_svc.import_upload(
        registry,
        contents=contents,
        filename=file.filename,
        user_id=user.id,
        format=format,
        options=options,
    )
    return ImportResultResponse(
        batch_id=result.batch_id,
        format=result.format,
        profile=result.profile,
        row_count=result.row_count,
        error_count=result.error_count,
        preview=result.preview,
        errors=[
            ImportRowErrorResponse.model_validate(error) for error in result.errors
        ],
    )


@router.get(
    "/batches",
    response_model=ImportBatchListResponse,
    summary="List import batches",
    description=requires_capability("data-extract", "read"),
)
async def list_import_batches(
    registry: DbRegistry,
    user: AuthorizedUser,
    page: Annotated[int, Query(ge=1)] = 1,
    per_page: Annotated[int, Query(ge=1, le=100)] = DEFAULT_PER_PAGE,
) -> ImportBatchListResponse:
    offset, limit = paginate_params(page, per_page)
    result = await data_import_svc.list_batches(
        registry,
        user,
        offset=offset,
        limit=limit,
    )
    items = [ImportBatchResponse.model_validate(batch) for batch in result.items]
    safe_page = max(1, page)
    return build_paginated(
        items,
        total=result.total,
        page=safe_page,
        per_page=limit,
    )


@router.get(
    "/batches/{batch_id}",
    response_model=ImportBatchDetailResponse,
    summary="Get import batch summary",
    description=requires_capability("data-extract", "read"),
)
async def get_import_batch(
    batch_id: Annotated[int, Path(description="Import batch id")],
    registry: DbRegistry,
    user: AuthorizedUser,
) -> ImportBatchDetailResponse:
    batch, rows = await data_import_svc.get_batch_summary(
        registry,
        batch_id,
        user,
    )
    return ImportBatchDetailResponse(
        batch=ImportBatchResponse.model_validate(batch),
        preview_rows=[ImportRowResponse.model_validate(row) for row in rows],
    )


@router.post(
    "/batches/{batch_id}/promote",
    response_model=PromoteBatchResponse,
    summary="Promote staged rows into domain storage",
    description=requires_capability("data-extract", "write"),
    dependencies=[Depends(require_capability("data-extract", "write"))],
)
async def promote_import_batch(
    batch_id: Annotated[int, Path(description="Import batch id")],
    registry: DbRegistry,
    user: AuthorizedUser,
) -> PromoteBatchResponse:
    result = await data_import_svc.promote_batch(registry, batch_id, user)
    return PromoteBatchResponse(
        batch_id=batch_id,
        promoted=result.promoted,
        skipped=result.skipped,
        errors=result.errors,
    )
