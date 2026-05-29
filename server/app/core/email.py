"""Pluggable email backend with protocol-based abstraction."""

import asyncio
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from html import escape
from typing import Protocol

from app.core.logging import logger
from app.settings import Settings, get_settings


class EmailBackend(Protocol):
    async def send(self, to: str, subject: str, html: str) -> None: ...


class ConsoleBackend:
    """Prints emails to stdout -- used in development."""

    async def send(self, to: str, subject: str, html: str) -> None:
        logger.info(
            "Email sent (console)",
            context={"to": to, "subject": subject, "body_preview": html[:200]},
        )


class SMTPBackend:
    """Generic SMTP backend."""

    async def send(self, to: str, subject: str, html: str) -> None:
        settings = get_settings()
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = settings.SMTP_FROM
        msg["To"] = to
        msg.attach(MIMEText(html, "html"))

        try:
            await asyncio.to_thread(self._send_sync, settings, to, msg)
        except smtplib.SMTPException:
            logger.error(
                "SMTP send failed",
                context={"to": to, "subject": subject},
            )
            raise

        logger.info("Email sent (SMTP)", context={"to": to, "subject": subject})

    def _send_sync(self, settings: Settings, to: str, msg: MIMEMultipart) -> None:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_FROM, to, msg.as_string())


def get_email_backend() -> EmailBackend:
    settings = get_settings()
    if settings.EMAIL_BACKEND == "smtp":
        return SMTPBackend()
    return ConsoleBackend()


def _wrap_email(title: str, body: str) -> str:
    """Shared HTML email wrapper -- single source for layout."""
    return (
        "<div style=\"font-family:'Roboto Mono',monospace;max-width:480px;"
        "margin:0 auto;padding:24px;background:#1a1a1a;color:#f5f5f5;"
        'border-radius:8px;">'
        f'<h2 style="color:#f97316;">{escape(title)}</h2>'
        f"{body}"
        '<hr style="border-color:#3a3a3a;margin-top:24px;">'
        '<p style="font-size:12px;color:#a3a3a3;">— gLOrng</p>'
        "</div>"
    )


def render_verification_email(token: str, base_url: str) -> str:
    url = f"{escape(base_url)}/api/auth/verify?token={escape(token)}"
    return _wrap_email(
        "Verify your email",
        f"<p>Click the link below to verify your account:</p>"
        f'<a href="{url}" style="color:#f97316;">{url}</a>'
        f'<p style="color:#a3a3a3;font-size:12px;">Expires in 24 hours.</p>',
    )


def render_reset_email(token: str, base_url: str) -> str:
    url = f"{escape(base_url)}/reset-password?token={escape(token)}"
    return _wrap_email(
        "Reset your password",
        f"<p>Click the link below to reset your password:</p>"
        f'<a href="{url}" style="color:#f97316;">{url}</a>'
        f'<p style="color:#a3a3a3;font-size:12px;">Expires in 1 hour.</p>',
    )
