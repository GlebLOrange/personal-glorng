"""Backward-compatible CLI shim for multicooker recipe seeding."""

from app.db.seed.cli.multicooker import main, seed_multicooker_recipes

__all__ = ["main", "seed_multicooker_recipes"]

if __name__ == "__main__":
    main()
