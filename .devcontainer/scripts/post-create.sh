#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$repo_root"

cd server
uv sync --frozen

cd ../client
npm ci

cd ../server
uv run python -m app.db.seed || true
