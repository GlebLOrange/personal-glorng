#!/usr/bin/env bash
# Detect symlinks outside dependency dirs and ancestor-pointing directory links.
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root"

allowed_prefixes=(
  "./client/node_modules/"
  "./server/.venv/"
)

is_allowed() {
  local path="$1"
  for prefix in "${allowed_prefixes[@]}"; do
    if [[ "$path" == "$prefix"* ]]; then
      return 0
    fi
  done
  return 1
}

errors=0

while IFS= read -r -d '' link; do
  rel="./${link#./}"
  if is_allowed "$rel"; then
    continue
  fi

  echo "unexpected symlink: $rel"
  errors=$((errors + 1))

  if [[ -d "$link" ]]; then
    target="$(readlink "$link" || true)"
    if [[ -n "$target" && "$target" != /* ]]; then
      resolved="$(cd "$(dirname "$link")" && cd "$target" 2>/dev/null && pwd -P)" || continue
      link_dir="$(cd "$(dirname "$link")" && pwd -P)"
      case "$resolved" in
        "$link_dir"|"$link_dir"/*)
          echo "  ancestor cycle: $rel -> $target"
          ;;
      esac
    fi
  fi
done < <(find . -type l -print0 2>/dev/null)

if [[ "$errors" -gt 0 ]]; then
  echo "found $errors unexpected symlink(s)"
  exit 1
fi

echo "no unexpected symlinks"
