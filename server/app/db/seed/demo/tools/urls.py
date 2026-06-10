"""Demo URL shortener seeding."""

from app.db.documents.user import User
from app.db.registry import DatabaseRegistry
from app.db.seed.builders.demo import build_short_url_seeds
from app.services.url import UrlService


async def seed_demo_short_urls(
    registry: DatabaseRegistry,
    count: int,
    owners: list[User],
) -> int:
    """Insert short URLs owned round-robin across demo users."""
    if registry.urls is None:
        msg = "URL repository is not initialized"
        raise RuntimeError(msg)

    svc = UrlService(registry)
    created = 0
    for index, seed in enumerate(build_short_url_seeds(count, seed=99)):
        owner = owners[index % len(owners)]
        url = await svc.create_short_url(
            original_url=seed.original_url,
            created_by=owner.id,
            title=seed.title,
        )
        if seed.clicks:
            await registry.urls.update_fields(url.id, clicks=seed.clicks)
        created += 1
    return created
