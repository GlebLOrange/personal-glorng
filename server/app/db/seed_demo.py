"""Backward-compatible CLI shim for demo seeding."""

from app.db.seed.cli.demo import main, parse_args
from app.db.seed.demo.run import seed_demo

__all__ = ["main", "parse_args", "seed_demo"]
