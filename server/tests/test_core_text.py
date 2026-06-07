from app.core.text import sanitize_optional_text, sanitize_text


def test_sanitize_text_strips_control_chars() -> None:
    assert sanitize_text("  buy\x00 milk  ") == "buy milk"


def test_sanitize_text_truncates() -> None:
    assert sanitize_text("abcdef", max_length=3) == "abc"


def test_sanitize_optional_text_returns_none_for_blank() -> None:
    assert sanitize_optional_text("   \x00  ") is None
