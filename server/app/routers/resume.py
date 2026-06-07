from typing import Any

from fastapi import APIRouter

from app.content.resume_data import RESUME_DATA

router = APIRouter()


@router.get(
    "",
    summary="Get resume data",
    description="Public portfolio resume content (skills, experience, projects).",
)
async def get_resume() -> dict[str, Any]:
    return RESUME_DATA
