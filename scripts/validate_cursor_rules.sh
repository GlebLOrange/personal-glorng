#!/usr/bin/env bash
# Validate .cursor/rules/*.mdc project rules.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RULES_DIR="$ROOT/.cursor/rules"
MAX_LINES=500
errors=0
warnings=0

err() {
  echo "ERROR: $*" >&2
  errors=$((errors + 1))
}

warn() {
  echo "WARN: $*" >&2
  warnings=$((warnings + 1))
}

if [[ ! -d "$RULES_DIR" ]]; then
  err "Missing rules directory: $RULES_DIR"
  exit 1
fi

# No .md files in rules/
while IFS= read -r -d '' md; do
  err "Unexpected .md file in rules (use .mdc): ${md#$ROOT/}"
done < <(find "$RULES_DIR" -maxdepth 1 -name '*.md' -print0)

shopt -s nullglob
mdc_files=("$RULES_DIR"/*.mdc)
shopt -u nullglob

if ((${#mdc_files[@]} == 0)); then
  err "No .mdc rule files found in $RULES_DIR"
fi

for file in "${mdc_files[@]}"; do
  base="$(basename "$file")"
  lines="$(wc -l < "$file" | tr -d ' ')"

  if ((lines > MAX_LINES)); then
    warn "$base exceeds $MAX_LINES lines ($lines)"
  fi

  # Frontmatter must exist with description and alwaysApply
  if ! awk '
    BEGIN { in_fm=0; has_desc=0; has_apply=0; fm_closed=0 }
    NR==1 && $0 != "---" { exit 1 }
    NR==1 && $0 == "---" { in_fm=1; next }
    in_fm && $0 == "---" { fm_closed=1; in_fm=0; next }
    in_fm && $0 ~ /^description:/ { has_desc=1 }
    in_fm && $0 ~ /^alwaysApply:/ { has_apply=1 }
    END { exit !(fm_closed && has_desc && has_apply) }
  ' "$file"; then
    err "$base: frontmatter must include description and alwaysApply"
  fi

  # Opt-in rules (no globs) should document relationship to always-on rules
  if grep -q '^alwaysApply: false' "$file" && ! grep -q '^globs:' "$file"; then
    if ! grep -q 'Relationship to other rules' "$file"; then
      err "$base: alwaysApply false but missing 'Relationship to other rules' section"
    fi
  fi

  # Cross-references to *.mdc files
  while IFS= read -r ref; do
    [[ -z "$ref" ]] && continue
    if [[ ! -f "$RULES_DIR/$ref" ]]; then
      err "$base: references missing rule file: $ref"
    fi
  done < <(grep -oE '`[a-z0-9-]+\.mdc`' "$file" | tr -d '`' | sort -u)
done

echo "Checked ${#mdc_files[@]} rule file(s) in .cursor/rules/"

if ((errors > 0)); then
  echo "Validation failed: $errors error(s), $warnings warning(s)" >&2
  exit 1
fi

if ((warnings > 0)); then
  echo "Validation passed with $warnings warning(s)"
else
  echo "Validation passed"
fi
