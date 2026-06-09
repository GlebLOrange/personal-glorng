from html import escape

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.core.email import _wrap_email
from app.core.text import sanitize_email_subject


class EmailSend(BaseModel):
    to: EmailStr
    subject: str = Field(
        min_length=1,
        max_length=255,
        description="Plain-text subject line (no line breaks).",
    )
    body: str = Field(min_length=1, max_length=5000)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "to": "user@example.com",
                "subject": "Hello from gLOrng",
                "body": "This is a test message.",
            }
        }
    )

    @field_validator("subject")
    @classmethod
    def validate_subject(cls, value: str) -> str:
        return sanitize_email_subject(value)


class EmailPreview(BaseModel):
    html: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"html": "<html><body><p>Preview</p></body></html>"},
        },
    )


def render_email_html(data: EmailSend) -> str:
    """Escape user body and wrap in the site email template."""
    safe_body = escape(data.body).replace("\n", "<br>")
    return _wrap_email(data.subject, f"<p>{safe_body}</p>")
