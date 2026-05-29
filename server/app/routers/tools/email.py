from html import escape

from fastapi import APIRouter, Depends
from pydantic import BaseModel, EmailStr, Field

from app.core.deps import AuthorizedUser, require_capability
from app.core.email import _wrap_email, get_email_backend

router = APIRouter(
    prefix="/email",
    dependencies=[Depends(require_capability("email", "write"))],
)


class EmailSend(BaseModel):
    to: EmailStr
    subject: str = Field(min_length=1, max_length=255)
    body: str = Field(min_length=1, max_length=5000)


class EmailPreview(BaseModel):
    html: str


def _render_email_html(data: EmailSend) -> str:
    """Escape user body and wrap in the site email template."""
    safe_body = escape(data.body).replace("\n", "<br>")
    return _wrap_email(data.subject, f"<p>{safe_body}</p>")


@router.post("/send")
async def send_email(data: EmailSend, _user: AuthorizedUser) -> dict[str, str]:
    """Send a freeform email wrapped in the site-styled template."""
    html = _render_email_html(data)
    backend = get_email_backend()
    await backend.send(data.to, data.subject, html)
    return {"detail": "Email sent"}


@router.post("/preview", response_model=EmailPreview)
async def preview_email(data: EmailSend, _user: AuthorizedUser) -> EmailPreview:
    """Return the rendered HTML without sending."""
    return EmailPreview(html=_render_email_html(data))
