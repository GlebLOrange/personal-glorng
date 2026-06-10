"""Create the default E2E admin user when missing (CI smoke tests)."""

import asyncio
import sys

from app.db.init_service import DatabaseInitService
from app.db.registry import DatabaseRegistry
from app.services.user import create_user, default_owner_permissions, get_user_by_email
from app.settings import get_settings


async def ensure_e2e_user() -> None:
    """Ensure admin@glorng.dev exists with known test credentials."""
    settings = get_settings()
    registry = DatabaseRegistry()
    init_svc = DatabaseInitService(registry, settings)
    try:
        await init_svc.startup()
        if registry.users is None:
            msg = "Users repository is not initialized"
            raise RuntimeError(msg)

        existing = await get_user_by_email(registry, settings.E2E_EMAIL)
        if existing:
            if not existing.is_protected:
                await registry.users.update_fields(existing.id, is_protected=True)
            return

        await create_user(
            registry,
            email=settings.E2E_EMAIL,
            password=settings.E2E_PASSWORD,
            permissions=default_owner_permissions(),
            is_verified=True,
            is_protected=True,
        )
    finally:
        await init_svc.shutdown()


def main() -> None:
    asyncio.run(ensure_e2e_user())


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print("ensure_e2e_user failed", file=sys.stderr)  # noqa: T201
        raise
