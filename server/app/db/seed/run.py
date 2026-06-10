"""Backward-compatible re-export for core seed orchestrator."""

from app.db.seed.core.admin import WEAK_PASSWORDS, require_repos, seed_admin
from app.db.seed.core.run import seed

# Legacy private names used by older imports
_require_repos = require_repos
_seed_admin = seed_admin

__all__ = ["WEAK_PASSWORDS", "_require_repos", "_seed_admin", "seed"]
