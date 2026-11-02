#!/usr/bin/env sh
# Pass/fail demo for check_staged_token_limit.sh (temp files only).
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
CHECK="$SCRIPT_DIR/check_staged_token_limit.sh"
IGNORE="$SCRIPT_DIR/staged-token-limit.ignore"
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

pass() {
	printf 'PASS: %s\n' "$1"
}

fail() {
	printf 'FAIL: %s\n' "$1" >&2
	exit 1
}

# Exactly 20_000 bytes => 5000 tokens => must pass (limit is exclusive >).
small="$TMP/small.py"
dd if=/dev/zero bs=20000 count=1 2>/dev/null | tr '\0' 'a' >"$small"
if ! sh "$CHECK" "$small" >/dev/null 2>&1; then
	fail "file at exactly 5000 tokens should pass"
fi
pass "exactly 5000 tokens exits 0"

# 20_004 bytes => 5001 tokens => must fail with path, count, limit, split advice.
big="$TMP/big_module.py"
dd if=/dev/zero bs=20004 count=1 2>/dev/null | tr '\0' 'b' >"$big"
out=$(mktemp)
if sh "$CHECK" "$big" >"$out" 2>&1; then
	fail "file over 5000 tokens should fail"
fi
grep -F "$big" "$out" >/dev/null || fail "error must name the offending file"
grep -E 'tokens:[[:space:]]*5001' "$out" >/dev/null || fail "error must show token count 5001"
grep -F '5000' "$out" >/dev/null || fail "error must mention the 5000 limit"
grep -E 'modules, classes, or functions' "$out" >/dev/null ||
	fail "error must include logical-boundary split instructions"
pass "oversized file fails with file, count, limit, and split instructions"

# Oversized lockfile name must be ignored.
lock="$TMP/uv.lock"
dd if=/dev/zero bs=30000 count=1 2>/dev/null | tr '\0' 'c' >"$lock"
STAGED_TOKEN_LIMIT_IGNORE="$IGNORE"
export STAGED_TOKEN_LIMIT_IGNORE
if ! sh "$CHECK" "$lock" >/dev/null 2>&1; then
	fail "oversized uv.lock should be ignored"
fi
pass "oversized uv.lock is ignored and exits 0"

printf '%s\n' "All check_staged_token_limit checks passed."
