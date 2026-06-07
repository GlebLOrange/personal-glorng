"""Create the default E2E admin user when missing (CI smoke tests)."""

import asyncio
import os
import sys

from sqlalchemy import select

from app.db.models.user import User
from app.db.session import get_session_factory
from app.services.user import create_user, default_owner_permissions

E2E_EMAIL = os.environ.get("E2E_EMAIL", "admin@glorng.dev")
E2E_PASSWORD = os.environ.get("E2E_PASSWORD", "MyTestPass123!")


async def ensure_e2e_user() -> None:
    """Ensure admin@glorng.dev exists with known test credentials."""
    factory = get_session_factory()
    async with factory() as db:
        result = await db.execute(select(User).where(User.email == E2E_EMAIL))
        if result.scalar_one_or_none():
            return
        await create_user(
            db,
            email=E2E_EMAIL,
            password=E2E_PASSWORD,
            permissions=default_owner_permissions(),
            is_verified=True,
        )
        await db.commit()


def main() -> None:
    asyncio.run(ensure_e2e_user())


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print("ensure_e2e_user failed", file=sys.stderr)  # noqa: T201
        raise
