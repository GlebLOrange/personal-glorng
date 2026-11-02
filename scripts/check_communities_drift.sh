#!/usr/bin/env bash
# Fail if the full Gortex Community Skills table leaks into always-on files.
# Canonical home: .cursor/references/gortex-communities.md
set -euo pipefail
cd "$(dirname "$0")/.."
fail=0
for f in AGENTS.md GEMINI.md .github/copilot-instructions.md .cursor/rules/gortex-communities.mdc .agents/rules/gortex-communities.md; do
  [ -f "$f" ] || continue
  if grep -nE 'gortex:communities|^#+ *Community Skills' "$f"; then
    echo "drift: Community Skills table/marker found in $f (keep it only in .cursor/references/gortex-communities.md)" >&2
    fail=1
  fi
done
exit $fail
