"""Password strength rules shared by auth and account flows."""

import re
from functools import lru_cache
from pathlib import Path

PASSWORD_MIN_LENGTH = 12
PASSWORD_PATTERN = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s]).{12,}$",
)
_PASSWORD_ERROR = (
    "Password must be 12+ chars with uppercase, lowercase, digit, and special"
)


@lru_cache(maxsize=1)
def _common_passwords() -> frozenset[str]:
    path = Path(__file__).with_name("common_passwords.txt")
    lines = path.read_text(encoding="utf-8").splitlines()
    return frozenset(line.strip().lower() for line in lines if line.strip())


def validate_password_strength(password: str) -> str:
    """Return password when it meets policy; raise ValueError otherwise."""
    if not PASSWORD_PATTERN.match(password):
        raise ValueError(_PASSWORD_ERROR)
    if password.lower() in _common_passwords():
        raise ValueError("Password is too common; choose a more unique password")
    return password
