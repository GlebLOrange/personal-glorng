"""Paths skipped for request logging and Mongo app-log persistence."""

PROBE_LOG_SKIP_PATHS = frozenset({"/api/health", "/api/ready"})
