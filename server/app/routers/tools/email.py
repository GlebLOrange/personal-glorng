"""Outbound email tool. All routes require `email:write`."""

import re
from html import escape

from fastapi import APIRouter, Depends
from pydantic import BaseModel, EmailStr, Field, field_validator

from app.core.deps import AuthorizedUser, require_capability
from app.core.email import _wrap_email, get_email_backend
from app.openapi import requires_capability

_CONTROL_CHARS = re.compile(r"[\x00-\x1f\x7f]")

router = APIRouter(
    prefix="/email",
    tags=["email"],
    dependencies=[Depends(require_capability("email", "write"))],
)


class EmailSend(BaseModel):
    to: EmailStr
    subject: str = Field(
        min_length=1,
        max_length=255,
        description="Plain-text subject line (no line breaks).",
    )
    body: str = Field(min_length=1, max_length=5000)

    @field_validator("subject")
    @classmethod
    def validate_subject(cls, value: str) -> str:
        if "\r" in value or "\n" in value:
            msg = "Subject must not contain line breaks"
            raise ValueError(msg)
        cleaned = _CONTROL_CHARS.sub("", value).strip()
        if not cleaned:
            msg = "Subject must not be empty"
            raise ValueError(msg)
        return cleaned


class EmailPreview(BaseModel):
    html: str


def _render_email_html(data: EmailSend) -> str:
    """Escape user body and wrap in the site email template."""
    safe_body = escape(data.body).replace("\n", "<br>")
    return _wrap_email(data.subject, f"<p>{safe_body}</p>")


@router.post(
    "/send",
    summary="Send email",
    description=requires_capability("email", "write"),
)
async def send_email(data: EmailSend, _user: AuthorizedUser) -> dict[str, str]:
    html = _render_email_html(data)
    plain = f"{data.subject}\n\n{data.body}\n\n— gLOrng\n"
    backend = get_email_backend()
    await backend.send(data.to, data.subject, html, plain)
    return {"detail": "Email sent"}


@router.post(
    "/preview",
    response_model=EmailPreview,
    summary="Preview email HTML",
    description=requires_capability("email", "write"),
)
async def preview_email(data: EmailSend, _user: AuthorizedUser) -> EmailPreview:
    return EmailPreview(html=_render_email_html(data))
