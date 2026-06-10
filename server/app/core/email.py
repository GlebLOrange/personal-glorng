"""Pluggable email backend with protocol-based abstraction."""

import asyncio
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from html import escape
from typing import Protocol

from app.core.logging import logger
from app.settings import Settings, get_settings

EMAIL_COLORS = {
    "surface_dark": "#141820",
    "surface_card": "#1c2230",
    "surface_border": "#2e3a4e",
    "surface_light": "#f5f2ec",
    "surface_mid": "#c4b8ac",
    "surface_muted": "#8a847e",
    "accent_blue": "#7bbde2",
    "accent_violet": "#b8a3c8",
}

FONT_STACK = "'IBM Plex Sans', system-ui, sans-serif"
SITE_NAME = "Gleb.Y"


class EmailBackend(Protocol):
    async def send(
        self,
        to: str,
        subject: str,
        html: str,
        plain: str | None = None,
    ) -> None: ...


class ConsoleBackend:
    """Prints emails to stdout -- used in development."""

    async def send(
        self,
        to: str,
        subject: str,
        html: str,
        plain: str | None = None,
    ) -> None:
        logger.info(
            "Email sent (console)",
            context={
                "to": to,
                "subject": subject,
                "html_bytes": len(html.encode("utf-8")),
                "plain_bytes": len((plain or "").encode("utf-8")),
            },
        )


class SMTPBackend:
    """Generic SMTP backend."""

    async def send(
        self,
        to: str,
        subject: str,
        html: str,
        plain: str | None = None,
    ) -> None:
        settings = get_settings()
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = settings.SMTP_FROM
        msg["To"] = to
        if plain:
            msg.attach(MIMEText(plain, "plain", "utf-8"))
        msg.attach(MIMEText(html, "html", "utf-8"))

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


def render_plain_text(title: str, body_lines: list[str]) -> str:
    """Plain-text email body for multipart messages."""
    body = "\n".join(body_lines)
    return f"{title}\n\n{body}\n\n— {SITE_NAME}\n"


def _cta_button(href: str, label: str) -> str:
    colors = EMAIL_COLORS
    safe_href = escape(href, quote=True)
    safe_label = escape(label)
    return (
        '<table role="presentation" cellspacing="0" cellpadding="0" border="0" '
        'style="margin:24px 0;">'
        "<tr><td "
        f'style="border-radius:8px;background:{colors["accent_blue"]};">'
        f'<a href="{safe_href}" target="_blank" '
        f'style="display:inline-block;padding:12px 24px;font-family:{FONT_STACK};'
        f"font-size:14px;font-weight:600;color:{colors['surface_dark']};"
        'text-decoration:none;border-radius:8px;">'
        f"{safe_label}</a></td></tr></table>"
    )


def _fallback_link(url: str) -> str:
    colors = EMAIL_COLORS
    safe_href = escape(url, quote=True)
    safe_display = escape(url)
    link_style = "margin:0;font-family:monospace;font-size:12px;word-break:break-all;"
    return (
        f'<p style="margin:16px 0 4px;font-family:{FONT_STACK};font-size:13px;'
        f'color:{colors["surface_mid"]};">Or copy this link:</p>'
        f'<p style="{link_style}">'
        f'<a href="{safe_href}" style="color:{colors["accent_blue"]};">'
        f"{safe_display}</a></p>"
    )


def _wrap_email(title: str, body: str, *, site_url: str | None = None) -> str:
    """Shared HTML email wrapper -- single source for layout."""
    colors = EMAIL_COLORS
    safe_title = escape(title)
    footer_url = ""
    if site_url:
        safe_site = escape(site_url.rstrip("/"))
        footer_url = (
            f'<p style="margin:4px 0 0;font-family:{FONT_STACK};font-size:11px;">'
            f'<a href="{escape(site_url.rstrip("/"), quote=True)}" '
            f'style="color:{colors["accent_blue"]};text-decoration:none;">'
            f"{safe_site}</a></p>"
        )
    return (
        f'<!DOCTYPE html><html><body style="margin:0;padding:0;'
        f'background:{colors["surface_dark"]};">'
        '<table role="presentation" width="100%" cellspacing="0" cellpadding="0" '
        f'border="0" style="background:{colors["surface_dark"]};padding:32px 16px;">'
        '<tr><td align="center">'
        '<table role="presentation" width="100%" cellspacing="0" cellpadding="0" '
        'border="0" style="max-width:560px;">'
        "<tr><td "
        f'style="background:{colors["surface_card"]};border:1px solid '
        f'{colors["surface_border"]};border-radius:8px;padding:32px;">'
        f'<p style="margin:0 0 8px;font-family:{FONT_STACK};font-size:18px;'
        f'font-weight:700;color:{colors["accent_blue"]};">{SITE_NAME}</p>'
        f'<div style="width:48px;height:3px;background:{colors["accent_blue"]};'
        f'margin-bottom:24px;border-radius:2px;"></div>'
        f'<h1 style="margin:0 0 16px;font-family:{FONT_STACK};font-size:22px;'
        f'font-weight:600;color:{colors["surface_light"]};">{safe_title}</h1>'
        f"{body}"
        f'<hr style="border:none;border-top:1px solid {colors["surface_border"]};'
        'margin:32px 0 16px;">'
        f'<p style="margin:0;font-family:{FONT_STACK};font-size:12px;'
        f'color:{colors["surface_muted"]};">— {SITE_NAME}</p>'
        f"{footer_url}"
        "</td></tr></table></td></tr></table></body></html>"
    )


def _verification_url(token: str, base_url: str) -> str:
    return f"{base_url.rstrip('/')}/verify-email?token={token}"


def _reset_url(token: str, base_url: str) -> str:
    return f"{base_url.rstrip('/')}/reset-password?token={token}"


def _body_text_style() -> str:
    colors = EMAIL_COLORS
    return (
        f"margin:0 0 16px;font-family:{FONT_STACK};font-size:15px;"
        f"line-height:1.5;color:{colors['surface_mid']};"
    )


def _expiry_note(hours: int) -> str:
    colors = EMAIL_COLORS
    label = "1 hour" if hours == 1 else f"{hours} hours"
    return (
        f'<p style="margin:24px 0 0;font-family:{FONT_STACK};font-size:12px;'
        f'color:{colors["surface_muted"]};">Link expires in {label}.</p>'
    )


def render_verification_email(token: str, base_url: str) -> str:
    url = _verification_url(token, base_url)
    body = (
        f'<p style="{_body_text_style()}">'
        "Welcome to Gleb.Y! Verify your email to activate your account."
        "</p>"
        f"{_cta_button(url, 'Verify email')}"
        f"{_fallback_link(url)}"
        f"{_expiry_note(24)}"
    )
    return _wrap_email("Verify your email", body, site_url=base_url)


def render_verification_email_plain(token: str, base_url: str) -> str:
    url = _verification_url(token, base_url)
    return render_plain_text(
        "Verify your email",
        [
            "Welcome to Gleb.Y!",
            "Verify your email to activate your account.",
            "",
            url,
            "",
            "Link expires in 24 hours.",
        ],
    )


def render_reset_email(token: str, base_url: str) -> str:
    url = _reset_url(token, base_url)
    body = (
        f'<p style="{_body_text_style()}">'
        "We received a request to reset your password. "
        "Click the button below to choose a new one."
        "</p>"
        f"{_cta_button(url, 'Reset password')}"
        f"{_fallback_link(url)}"
        f"{_expiry_note(1)}"
    )
    return _wrap_email("Reset your password", body, site_url=base_url)


def render_reset_email_plain(token: str, base_url: str) -> str:
    url = _reset_url(token, base_url)
    return render_plain_text(
        "Reset your password",
        [
            "We received a request to reset your password.",
            "Use the link below to choose a new one.",
            "",
            url,
            "",
            "Link expires in 1 hour.",
        ],
    )
