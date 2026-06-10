from html import escape

from app.core.email import (
    _wrap_email,
    render_plain_text,
    render_reset_email,
    render_reset_email_plain,
    render_verification_email,
    render_verification_email_plain,
)


def test_verification_email_uses_brand_colors() -> None:
    html = render_verification_email("test-token", "https://glorng.dev")
    assert "#141820" in html
    assert "#7bbde2" in html
    assert "#1c2230" in html


def test_verification_email_contains_verify_url() -> None:
    token = "abc123"
    base_url = "https://glorng.dev"
    html = render_verification_email(token, base_url)
    assert f"{base_url}/verify-email?token={token}" in html
    assert "Verify email" in html
    assert "Welcome to Gleb.Y" in html


def test_verification_email_escapes_malicious_token() -> None:
    token = '"><script>alert(1)</script>'
    html = render_verification_email(token, "https://glorng.dev")
    assert "<script>" not in html
    assert escape(token) in html


def test_reset_email_contains_reset_url_and_brand_colors() -> None:
    token = "reset-token"
    base_url = "https://glorng.dev"
    html = render_reset_email(token, base_url)
    assert f"{base_url}/reset-password?token={token}" in html
    assert "#141820" in html
    assert "#7bbde2" in html
    assert "Reset password" in html


def test_wrap_email_escapes_title() -> None:
    html = _wrap_email("<script>alert(1)</script>", "<p>Body</p>")
    assert "<script>" not in html
    assert escape("<script>alert(1)</script>") in html


def test_verification_plain_text_includes_url() -> None:
    token = "plain-token"
    base_url = "https://glorng.dev"
    plain = render_verification_email_plain(token, base_url)
    assert f"{base_url}/verify-email?token={token}" in plain
    assert "Verify your email" in plain
    assert "24 hours" in plain


def test_reset_plain_text_includes_url() -> None:
    token = "plain-reset"
    base_url = "https://glorng.dev"
    plain = render_reset_email_plain(token, base_url)
    assert f"{base_url}/reset-password?token={token}" in plain
    assert "1 hour" in plain


def test_render_plain_text_format() -> None:
    plain = render_plain_text("Hello", ["Line one", "Line two"])
    assert plain.startswith("Hello\n\n")
    assert "Line one" in plain
    assert plain.endswith("— Gleb.Y\n")
