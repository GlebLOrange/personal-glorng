#!/usr/bin/env bash
# Create the next ADR from the template. Usage: make adr-new TITLE="short title"
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ADR_DIR="$ROOT/docs/adr"
TEMPLATE="$ADR_DIR/0000-template.md"
TITLE="${TITLE:-${1:-}}"

if [[ -z "$TITLE" ]]; then
  echo "Usage: make adr-new TITLE=\"short title\"" >&2
  exit 1
fi

if [[ ! -f "$TEMPLATE" ]]; then
  echo "missing template: $TEMPLATE" >&2
  exit 1
fi

slug="$(printf '%s' "$TITLE" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g; s/^-+//; s/-+$//; s/-+/-/g')"
if [[ -z "$slug" ]]; then
  echo "could not derive slug from TITLE" >&2
  exit 1
fi

next=1
for existing in "$ADR_DIR"/[0-9][0-9][0-9][0-9]-*.md; do
  [[ -e "$existing" ]] || continue
  base="$(basename "$existing")"
  num="${base%%-*}"
  if [[ "$num" =~ ^[0-9]+$ ]] && ((10#$num >= next)) && [[ "$num" != "0000" ]]; then
    next=$((10#$num + 1))
  fi
done

num_padded="$(printf '%04d' "$next")"
dest="$ADR_DIR/${num_padded}-${slug}.md"

if [[ -e "$dest" ]]; then
  echo "already exists: $dest" >&2
  exit 1
fi

{
  echo "# ADR ${num_padded}: ${TITLE}"
  echo
  # Skip the template H1; keep Status/Context/Decision/Consequences body.
  tail -n +3 "$TEMPLATE"
} >"$dest"

echo "created ${dest#$ROOT/}"
echo "Add it to docs/adr/index.md and the VitePress ADR sidebar."
