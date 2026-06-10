"""Backward-compatible re-exports for demo seed builders."""

from app.db.seed.builders.demo import (
    DEMO_READER_EMAIL,
    DEMO_WRITER_EMAIL,
    ShortUrlSeed,
    build_random_feedback,
    build_random_recipes,
    build_random_tasks,
    build_recipe_tag_pool,
    build_short_url_seeds,
    demo_reader_permissions,
    demo_writer_permissions,
)

__all__ = [
    "DEMO_READER_EMAIL",
    "DEMO_WRITER_EMAIL",
    "ShortUrlSeed",
    "build_random_feedback",
    "build_random_recipes",
    "build_random_tasks",
    "build_recipe_tag_pool",
    "build_short_url_seeds",
    "demo_reader_permissions",
    "demo_writer_permissions",
]
