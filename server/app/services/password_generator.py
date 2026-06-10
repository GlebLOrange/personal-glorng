"""Cryptographically secure password generation for the public tool."""

import secrets
import string

from app.core.exceptions import ValidationError

SYMBOLS = "!@#$%^&*()-_=+[]{}|;:,.<>?"
AMBIGUOUS = "0O1lI"

_LOWERCASE = string.ascii_lowercase
_UPPERCASE = string.ascii_uppercase
_DIGITS = string.digits


def _apply_ambiguous_filter(charset: str, exclude_ambiguous: bool) -> str:
    if not exclude_ambiguous:
        return charset
    return "".join(c for c in charset if c not in AMBIGUOUS)


def _build_charsets(
    *,
    uppercase: bool,
    lowercase: bool,
    digits: bool,
    symbols: bool,
    exclude_ambiguous: bool,
) -> list[str]:
    groups: list[str] = []
    if lowercase:
        groups.append(_apply_ambiguous_filter(_LOWERCASE, exclude_ambiguous))
    if uppercase:
        groups.append(_apply_ambiguous_filter(_UPPERCASE, exclude_ambiguous))
    if digits:
        groups.append(_apply_ambiguous_filter(_DIGITS, exclude_ambiguous))
    if symbols:
        groups.append(_apply_ambiguous_filter(SYMBOLS, exclude_ambiguous))
    return [g for g in groups if g]


def generate_password(
    length: int,
    *,
    uppercase: bool = True,
    lowercase: bool = True,
    digits: bool = True,
    symbols: bool = True,
    exclude_ambiguous: bool = False,
) -> str:
    """Return a random password using secrets with guaranteed charset coverage."""
    groups = _build_charsets(
        uppercase=uppercase,
        lowercase=lowercase,
        digits=digits,
        symbols=symbols,
        exclude_ambiguous=exclude_ambiguous,
    )
    if not groups:
        raise ValidationError("At least one character set must be selected")

    union = "".join(groups)
    if not union:
        raise ValidationError("Selected character sets are empty after filtering")

    if length < len(groups):
        raise ValidationError(
            f"Length must be at least {len(groups)} for the selected character sets"
        )

    chars = [secrets.choice(group) for group in groups]
    for _ in range(length - len(groups)):
        chars.append(secrets.choice(union))

    secrets.SystemRandom().shuffle(chars)
    return "".join(chars)
