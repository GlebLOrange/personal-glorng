from typing import Any

from fastapi import APIRouter, Depends
from fastapi.responses import Response

from app.content.resume_data import RESUME_DATA
from app.core.rate_limit import rate_limit_api
from app.core.utils import attachment_content_disposition
from app.db.deps import DbRegistry
from app.services.github_portfolio import get_public_github_repos
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
    username, repos = await get_public_github_repos(
        get_settings(),
        registry=registry,
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
    pdf = await get_cached_resume_pdf(dict(RESUME_DATA))
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition": attachment_content_disposition("gleb.y.cv.pdf"),
        },
    )
