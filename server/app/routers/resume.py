from typing import Any

from fastapi import APIRouter, Depends
from fastapi.responses import Response

from app.content.resume_data import RESUME_DATA
from app.core.rate_limit import rate_limit_api
from app.core.utils import attachment_content_disposition
from app.db.deps import DbRegistry
from app.services.github_portfolio import get_public_github_repos
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
    # #region agent log
    import json
    import time

    def _dbg_resume(location: str, message: str, data: dict, hypothesis_id: str) -> None:
        with open(
            "/Users/glorange/projects/portfolio-glorng/.cursor/debug-27ee16.log",
            "a",
            encoding="utf-8",
        ) as _f:
            _f.write(
                json.dumps(
                    {
                        "sessionId": "27ee16",
                        "location": location,
                        "message": message,
                        "data": data,
                        "timestamp": int(time.time() * 1000),
                        "hypothesisId": hypothesis_id,
                    }
                )
                + "\n"
            )

    _dbg_resume(
        "resume.py:download_resume_pdf:entry",
        "PDF download handler entered",
        {},
        "H2",
    )
    # #endregion
    try:
        from app.services.resume_pdf import render_resume_pdf

        # #region agent log
        _dbg_resume(
            "resume.py:download_resume_pdf:pre-render",
            "WeasyPrint import succeeded, starting render",
            {},
            "H3",
        )
        # #endregion
        pdf = render_resume_pdf(dict(RESUME_DATA))
        # #region agent log
        _dbg_resume(
            "resume.py:download_resume_pdf:post-render",
            "PDF render completed",
            {"pdf_bytes": len(pdf)},
            "H2",
        )
        # #endregion
    except Exception as exc:
        # #region agent log
        _dbg_resume(
            "resume.py:download_resume_pdf:error",
            "PDF render failed",
            {"error_type": type(exc).__name__, "error": str(exc)[:500]},
            "H3",
        )
        # #endregion
        raise
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition": attachment_content_disposition("Gleb.Y-CV.pdf"),
        },
    )
