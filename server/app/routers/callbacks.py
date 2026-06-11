"""OAuth callback endpoints (Google Calendar)."""

from aiogram import Bot
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow

from app.core.google_oauth_state import consume_google_oauth_state
from app.core.logging import logger
from app.db.deps import DbRegistry
from app.db.documents.credential import GoogleCredential
from app.settings import get_settings

router = APIRouter()

_SUCCESS_HTML = """
<html><body style="font-family:sans-serif;text-align:center;padding:40px">
<h2>Connected!</h2>
<p>Google Calendar is linked. You can close this tab.</p>
</body></html>
"""

_ERROR_HTML = """
<html><body style="font-family:sans-serif;text-align:center;padding:40px">
<h2>Error</h2>
<p>Something went wrong. Please try again from Telegram.</p>
</body></html>
"""


@router.get(
    "/google",
    summary="Google OAuth callback",
    description="Exchange Google Calendar OAuth code and store refresh token.",
)
async def google_oauth_callback(
    code: str,
    state: str,
    registry: DbRegistry,
) -> HTMLResponse:
    """Exchange OAuth code for refresh token and store it."""
    settings = get_settings()

    if registry.credentials is None:
        return HTMLResponse(_ERROR_HTML, status_code=500)

    telegram_user_id = await consume_google_oauth_state(state)
    if telegram_user_id is None:
        return HTMLResponse(_ERROR_HTML, status_code=400)

    try:
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/v2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                },
            },
            scopes=["https://www.googleapis.com/auth/calendar"],
            redirect_uri=settings.GOOGLE_REDIRECT_URI,
        )
        flow.fetch_token(code=code)
        credentials: Credentials = flow.credentials

        if not credentials.refresh_token:
            return HTMLResponse(_ERROR_HTML, status_code=400)

        from app.services.google_credentials import store_google_refresh_token

        encrypted_token = store_google_refresh_token(credentials.refresh_token)
        existing = await registry.credentials.get_google_for_telegram_user(
            telegram_user_id,
        )

        if existing:
            existing.refresh_token = encrypted_token
            await registry.credentials.upsert_google(existing)
        else:
            cred = GoogleCredential(
                id=0,
                telegram_user_id=telegram_user_id,
                refresh_token=encrypted_token,
            )
            await registry.credentials.upsert_google(cred)

        if settings.TELEGRAM_BOT_TO_DO_TOKEN:
            bot = Bot(token=settings.TELEGRAM_BOT_TO_DO_TOKEN)
            try:
                await bot.send_message(
                    chat_id=telegram_user_id,
                    text="Google Calendar connected successfully!",
                )
            finally:
                await bot.session.close()

        logger.info(
            "Google Calendar connected",
            context={"telegram_user_id": telegram_user_id},
        )

        return HTMLResponse(_SUCCESS_HTML)

    except Exception as exc:
        logger.error("Google OAuth callback failed", error=exc)
        return HTMLResponse(_ERROR_HTML, status_code=500)
