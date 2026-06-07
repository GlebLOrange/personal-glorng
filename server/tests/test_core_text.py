import pytest

from app.core.text import (
    sanitize_email_subject,
    sanitize_optional_text,
    sanitize_required_text,
    sanitize_text,
)


def test_sanitize_text_strips_control_chars() -> None:
    assert sanitize_text("  buy\x00 milk  ") == "buy milk"


def test_sanitize_text_truncates() -> None:
    assert sanitize_text("abcdef", max_length=3) == "abc"


def test_sanitize_optional_text_returns_none_for_blank() -> None:
    assert sanitize_optional_text("   \x00  ") is None


def test_sanitize_required_text_rejects_blank() -> None:
    with pytest.raises(ValueError, match="Text must not be empty"):
        sanitize_required_text("   \x00  ")


def test_sanitize_required_text_strips_control_chars() -> None:
    assert sanitize_required_text("  hi\x00 there  ") == "hi there"


def test_sanitize_email_subject_rejects_crlf() -> None:
    with pytest.raises(ValueError, match="line breaks"):
        sanitize_email_subject("Hi\r\nBcc: evil@example.com")


def test_sanitize_email_subject_strips_control_chars() -> None:
    assert sanitize_email_subject("  Hello\x00  ") == "Hello"
