#!/usr/bin/env sh
# ponytail: thin wrapper so DSH and Cursor share one Gortex launch shape; upgrade path is env overrides.
set -eu

GORTEX="${GORTEX_BIN:-}"
if [ -z "$GORTEX" ]; then
  GORTEX="$(command -v gortex)" || {
    echo "run-gortex-mcp.sh: gortex not found; set GORTEX_BIN" >&2
    exit 127
  }
fi

# ponytail: daemon holds repo index; --index on mcp is deprecated when proxying.
exec "$GORTEX" mcp --proxy "$@"
