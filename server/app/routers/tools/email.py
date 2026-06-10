"""Outbound email tool. All routes require `email:write`."""

from fastapi import APIRouter, Depends

from app.core.deps import AuthorizedUser, require_capability
from app.core.email import get_email_backend
from app.openapi import requires_capability
from app.schemas.common import MessageResponse
from app.schemas.email import EmailPreview, EmailSend, render_email_html

router = APIRouter(
    prefix="/email",
    tags=["email"],
    dependencies=[Depends(require_capability("email", "write"))],
)


@router.post(
    "/send",
    response_model=MessageResponse,
    summary="Send email",
    description=requires_capability("email", "write"),
)
async def send_email(data: EmailSend, _user: AuthorizedUser) -> MessageResponse:
    html = render_email_html(data)
    plain = f"{data.subject}\n\n{data.body}\n\n— Gleb.Y\n"
    backend = get_email_backend()
    await backend.send(data.to, data.subject, html, plain)
    return MessageResponse(message="Email sent")


@router.post(
    "/preview",
    response_model=EmailPreview,
    summary="Preview email HTML",
    description=requires_capability("email", "write"),
)
async def preview_email(data: EmailSend, _user: AuthorizedUser) -> EmailPreview:
    return EmailPreview(html=render_email_html(data))
