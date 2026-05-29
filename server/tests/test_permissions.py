"""Tests for permission helpers."""

import pytest

from app.core.permissions import (
    SUPERUSER_PERMISSION,
    permission_key,
    user_has_permission,
)
from app.db.models.user import User


def test_superuser_implies_all() -> None:
    user = User(
        email="a@b.c",
        hashed_password="x",  # noqa: S106
        permissions=[SUPERUSER_PERMISSION],
    )
    assert user_has_permission(user, permission_key("tasks", "write"))


def test_explicit_permission() -> None:
    user = User(
        email="a@b.c",
        hashed_password="x",  # noqa: S106
        permissions=[permission_key("tasks", "read")],
    )
    assert user_has_permission(user, permission_key("tasks", "read"))
    assert not user_has_permission(user, permission_key("tasks", "write"))


def test_validate_permissions_rejects_unknown() -> None:
    from app.core.permissions import validate_permissions

    with pytest.raises(ValueError, match="Unknown permissions"):
        validate_permissions(["not-a-real:perm"])
