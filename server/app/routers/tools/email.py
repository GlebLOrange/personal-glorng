from html import escape

from fastapi import APIRouter, Depends
from pydantic import BaseModel, EmailStr

from app.core.deps import AdminUser, require_admin
from app.core.email import _wrap_email, get_email_backend

router = APIRouter(prefix="/email", dependencies=[Depends(require_admin)])


class EmailSend(BaseModel):
    to: EmailStr
    subject: str
    body: str


class EmailPreview(BaseModel):
    html: str


@router.post("/send")
async def send_email(data: EmailSend, _user: AdminUser) -> dict[str, str]:
    """Send a freeform email wrapped in the site-styled template."""
    safe_body = escape(data.body).replace("\n", "<br>")
    html = _wrap_email(data.subject, f"<p>{safe_body}</p>")
    backend = get_email_backend()
    await backend.send(data.to, data.subject, html)
    return {"detail": "Email sent"}


@router.post("/preview", response_model=EmailPreview)
async def preview_email(data: EmailSend, _user: AdminUser) -> EmailPreview:
    """Return the rendered HTML without sending."""
    safe_body = escape(data.body).replace("\n", "<br>")
    html = _wrap_email(data.subject, f"<p>{safe_body}</p>")
    return EmailPreview(html=html)
