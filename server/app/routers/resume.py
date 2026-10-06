"""Public resume API — JSON payload, PDF, Markdown, recruiter text, filtered profile."""

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query
from fastapi.responses import PlainTextResponse, Response

from app.content.resume_data import RESUME_DATA, RESUME_DOCUMENT
from app.core.rate_limit import rate_limit_api
from app.core.utils import attachment_content_disposition
from app.db.deps import DbRegistry
from app.schemas.resume import ResumeProfileSelection
from app.services.github_portfolio import get_public_github_repos
from app.services.resume_export import (
    build_recruiter_profile,
    render_resume_markdown,
    resume_dict_for_pdf,
    resume_json_bytes,
    select_resume,
)
from app.services.resume_pdf import get_cached_resume_pdf
from app.settings import get_settings

router = APIRouter()


@router.get(
    "",
    summary="Get resume data",
    description="Public portfolio resume content (skills, experience, projects).",
    dependencies=[Depends(rate_limit_api)],
)
async def get_resume(registry: DbRegistry) -> dict[str, Any]:
    data: dict[str, Any] = dict(RESUME_DATA)
    # Cache-only: never block the CV payload on a cold GitHub HTTP miss.
    # Client fills the strip via GET /github/repos when repos are empty.
    username, repos = await get_public_github_repos(
        get_settings(),
        registry=registry,
        cache_only=True,
    )
    data["github"] = {
        "enabled": bool(username and repos),
        "username": username,
        "repos": [repo.model_dump() for repo in repos],
    }
    return data


@router.get(
    "/pdf",
    summary="Download resume PDF",
    description="Generate and download the public portfolio resume as a PDF.",
    dependencies=[Depends(rate_limit_api)],
)
async def download_resume_pdf() -> Response:
    pdf = await get_cached_resume_pdf(resume_dict_for_pdf())
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition": attachment_content_disposition("gleb.y.cv.pdf"),
        },
    )


@router.get(
    "/markdown",
    summary="Download resume Markdown",
    description="Download the canonical resume as a Markdown file.",
    dependencies=[Depends(rate_limit_api)],
)
async def download_resume_markdown() -> Response:
    body = render_resume_markdown(RESUME_DOCUMENT).encode("utf-8")
    return Response(
        content=body,
        media_type="text/markdown; charset=utf-8",
        headers={
            "Content-Disposition": attachment_content_disposition("gleb.y.cv.md"),
        },
    )


@router.get(
    "/json",
    summary="Download resume JSON",
    description="Download the canonical resume as structured JSON.",
    dependencies=[Depends(rate_limit_api)],
)
async def download_resume_json() -> Response:
    return Response(
        content=resume_json_bytes(RESUME_DOCUMENT),
        media_type="application/json",
        headers={
            "Content-Disposition": attachment_content_disposition("gleb.y.cv.json"),
        },
    )


@router.get(
    "/recruiter-profile",
    summary="Get recruiter profile text",
    description="Concise recruiter-friendly profile derived from the canonical resume.",
    response_class=PlainTextResponse,
    dependencies=[Depends(rate_limit_api)],
)
async def get_recruiter_profile() -> PlainTextResponse:
    return PlainTextResponse(build_recruiter_profile(RESUME_DOCUMENT))


@router.get(
    "/profile",
    summary="Get filtered shareable resume profile",
    description=(
        "Return a subset of the canonical resume for shareable URLs. "
        "Unknown skill/project/section ids are ignored. Empty selections "
        "fall back to the full profile."
    ),
    response_model=ResumeProfileSelection,
    dependencies=[Depends(rate_limit_api)],
)
async def get_resume_profile(
    skills: Annotated[
        str | None,
        Query(description="Comma-separated skill ids"),
    ] = None,
    projects: Annotated[
        str | None,
        Query(description="Comma-separated project slugs"),
    ] = None,
    sections: Annotated[
        str | None,
        Query(description="Comma-separated section ids"),
    ] = None,
) -> ResumeProfileSelection:
    return select_resume(
        RESUME_DOCUMENT,
        skills=skills,
        projects=projects,
        sections=sections,
    )
