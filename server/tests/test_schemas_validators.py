import pytest

from app.schemas.validators import (
    validate_clean_optional,
    validate_clean_required,
    validate_clean_string_list,
)


def test_validate_clean_required_strips_control_chars() -> None:
    assert validate_clean_required("  hi\x00 there  ", field_name="Title") == "hi there"


def test_validate_clean_required_rejects_blank() -> None:
    with pytest.raises(ValueError, match="Title must not be empty"):
        validate_clean_required("   \x00  ", field_name="Title")


def test_validate_clean_optional_returns_none_for_blank() -> None:
    assert validate_clean_optional("   \x00  ") is None


def test_validate_clean_string_list_sanitizes_each_item() -> None:
    result = validate_clean_string_list(["  a\x00  ", "b"])
    assert result == ["a", "b"]
