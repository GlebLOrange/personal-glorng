from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from app.content.resume_data import RESUME_DATA
from app.services.amp_page import render_portfolio_amp
from app.settings import get_settings

router = APIRouter(tags=["amp"])


@router.get(
    "/amp",
    response_class=HTMLResponse,
    summary="Get AMP portfolio page",
    description="Public AMP HTML mirror of the portfolio.",
)
async def portfolio_amp() -> HTMLResponse:
    settings = get_settings()
    canonical = settings.BASE_URL.rstrip("/") + "/"
    html = render_portfolio_amp(RESUME_DATA, canonical)
    return HTMLResponse(content=html)
