from fastapi import APIRouter

from app.routers.auth import router as auth_router
from app.routers.callbacks import router as callbacks_router
from app.routers.donations import router as donations_router
from app.routers.feedback import router as feedback_router
from app.routers.github import router as github_router
from app.routers.resume import router as resume_router
from app.routers.spotify import router as spotify_router
from app.routers.tools import tools_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(github_router, prefix="/auth/github", tags=["github"])
api_router.include_router(resume_router, prefix="/resume", tags=["resume"])
api_router.include_router(
    donations_router,
    prefix="/donations",
    tags=["donations"],
)
api_router.include_router(
    spotify_router,
    prefix="/spotify",
    tags=["spotify"],
)
api_router.include_router(
    callbacks_router,
    prefix="/callbacks",
    tags=["callbacks"],
)
api_router.include_router(feedback_router)
api_router.include_router(tools_router)
