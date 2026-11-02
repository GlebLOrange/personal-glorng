#!/usr/bin/env sh
# Fail when a staged (or listed) text file exceeds 5000 tokens.
# Token estimate: 1 token = 4 bytes. See staged-token-limit.ignore for skips.
set -eu

LIMIT="${STAGED_TOKEN_LIMIT:-5000}"
BYTES_PER_TOKEN=4

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
IGNORE_FILE="${STAGED_TOKEN_LIMIT_IGNORE:-$SCRIPT_DIR/staged-token-limit.ignore}"

path_ignored() {
	_path=$1
	[ -f "$IGNORE_FILE" ] || return 1
	_base=$(basename -- "$_path")
	while IFS= read -r _pattern || [ -n "$_pattern" ]; do
		case "$_pattern" in
		'' | \#*) continue ;;
		esac
		_pattern=$(printf '%s' "$_pattern" | tr -d '\r')
		case "$_path" in
		$_pattern) return 0 ;;
		esac
		case "$_base" in
		$_pattern) return 0 ;;
		esac
	done <"$IGNORE_FILE"
	return 1
}

failed=0

check_file() {
	_path=$1
	[ -n "$_path" ] || return 0
	if path_ignored "$_path"; then
		return 0
	fi
	if [ ! -f "$_path" ]; then
		return 0
	fi
	_bytes=$(wc -c <"$_path" | tr -d ' ')
	_tokens=$(((_bytes + BYTES_PER_TOKEN - 1) / BYTES_PER_TOKEN))
	if [ "$_tokens" -gt "$LIMIT" ]; then
		printf '%s\n' "error: staged file exceeds token limit" >&2
		printf '  file:   %s\n' "$_path" >&2
		printf '  tokens: %s (limit %s; 1 token = %s bytes)\n' \
			"$_tokens" "$LIMIT" "$BYTES_PER_TOKEN" >&2
		printf '%s\n' "  Split this file into smaller files along logical boundaries:" >&2
		printf '%s\n' "  - modules, classes, or functions" >&2
		printf '%s\n' "  - configuration sections" >&2
		printf '%s\n' "  - documentation sections" >&2
		printf '%s\n' "  Then stage the new files and retry the commit." >&2
		failed=1
	fi
}

if [ "$#" -eq 0 ]; then
	while IFS= read -r path || [ -n "$path" ]; do
		check_file "$path"
	done <<EOF
$(git diff --cached --name-only --diff-filter=ACMR)
EOF
else
	for path in "$@"; do
		check_file "$path"
	done
fi

exit "$failed"
