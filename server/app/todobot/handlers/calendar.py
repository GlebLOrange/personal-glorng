"""Google Calendar OAuth connection handler."""

from urllib.parse import urlencode

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from app.settings import get_settings

router = Router()


@router.message(Command("connect_calendar"))
async def cmd_connect_calendar(message: Message) -> None:
    settings = get_settings()

    if not settings.GOOGLE_CLIENT_ID:
        await message.answer(
            "Google Calendar integration is not configured yet.",
        )
        return

    if not message.from_user:
        return

    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "https://www.googleapis.com/auth/calendar",
        "access_type": "offline",
        "prompt": "consent",
        "state": str(message.from_user.id),
    }

    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Connect Google Calendar",
                    url=auth_url,
                ),
            ],
        ],
    )

    await message.answer(
        "Click the button below to connect your Google Calendar:",
        reply_markup=keyboard,
    )
