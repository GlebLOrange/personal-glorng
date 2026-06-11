#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$repo_root"

if [[ ! -f .env ]]; then
  cp .env.example .env
fi

if grep -q '^JWT_SECRET=replace-with-a-strong-random-secret$' .env; then
  secret="$(openssl rand -base64 32 | tr -d '\n')"
  if sed --version >/dev/null 2>&1; then
    sed -i "s|^JWT_SECRET=.*|JWT_SECRET=${secret}|" .env
  else
    sed -i '' "s|^JWT_SECRET=.*|JWT_SECRET=${secret}|" .env
  fi
fi
