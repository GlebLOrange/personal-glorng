#!/usr/bin/env bash
# Install daily cron jobs for db_maintenance.sh (backup + stale check).
# Default: backup 04:20, stale check 12:00 Europe/Warsaw.
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root"

if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

BACKUP_TIMEZONE="${BACKUP_TIMEZONE:-Europe/Warsaw}"
CRON_SCHEDULE="${BACKUP_CRON_SCHEDULE:-20 4 * * *}"
STALE_CRON_SCHEDULE="${BACKUP_STALE_CRON_SCHEDULE:-0 12 * * *}"
LOG_FILE="${BACKUP_CRON_LOG:-$root/logs/backup.log}"
MAINTENANCE_SCRIPT="$root/scripts/db_maintenance.sh"
# Cron often has a minimal PATH; docker / docker compose must resolve.
CRON_PATH="${BACKUP_CRON_PATH:-/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin}"
CRON_HOME="${BACKUP_CRON_HOME:-${HOME:-$root}}"

if [[ ! -x "$MAINTENANCE_SCRIPT" ]]; then
  chmod +x "$MAINTENANCE_SCRIPT"
fi

mkdir -p "$(dirname "$LOG_FILE")"

existing="$(crontab -l 2>/dev/null || true)"
filtered="$(printf '%s\n' "$existing" | awk '
  /portfolio-glorng-db-maintenance-begin/ { skip=1; next }
  /portfolio-glorng-db-maintenance-end/ { skip=0; next }
  skip { next }
  { print }
')"

{
  printf '%s\n' "$filtered" | sed '/^$/d'
  printf '%s\n' "# portfolio-glorng-db-maintenance-begin"
  printf '%s\n' "CRON_TZ=${BACKUP_TIMEZONE}"
  printf '%s\n' "PATH=${CRON_PATH}"
  printf '%s\n' "HOME=${CRON_HOME}"
  printf '%s\n' "${CRON_SCHEDULE} cd ${root} && ${MAINTENANCE_SCRIPT} >> ${LOG_FILE} 2>&1"
  printf '%s\n' "${STALE_CRON_SCHEDULE} cd ${root} && ${MAINTENANCE_SCRIPT} --check-stale >> ${LOG_FILE} 2>&1"
  printf '%s\n' "# portfolio-glorng-db-maintenance-end"
} | crontab -

cat <<EOF
Installed daily DB maintenance cron jobs.

  Backup   : ${CRON_SCHEDULE} (${BACKUP_TIMEZONE})
  Stale    : ${STALE_CRON_SCHEDULE} (${BACKUP_TIMEZONE}) — alerts if LAST_SUCCESS is missing/old
  Script   : ${MAINTENANCE_SCRIPT}
  Log      : ${LOG_FILE}
  PATH     : ${CRON_PATH}
  HOME     : ${CRON_HOME}

Verify with: crontab -l | grep portfolio-glorng
Confirm docker is visible to cron: which docker (under the PATH above).

macOS launchd alternative (save as ~/Library/LaunchAgents/com.glorng.db-maintenance.plist):

<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>com.glorng.db-maintenance</string>
  <key>ProgramArguments</key>
  <array>
    <string>${MAINTENANCE_SCRIPT}</string>
  </array>
  <key>WorkingDirectory</key><string>${root}</string>
  <key>EnvironmentVariables</key>
  <dict>
    <key>PATH</key><string>${CRON_PATH}</string>
    <key>HOME</key><string>${CRON_HOME}</string>
  </dict>
  <key>StandardOutPath</key><string>${LOG_FILE}</string>
  <key>StandardErrorPath</key><string>${LOG_FILE}</string>
  <key>StartCalendarInterval</key>
  <dict>
    <key>Hour</key><integer>4</integer>
    <key>Minute</key><integer>20</integer>
  </dict>
  <key>TimeZone</key><string>${BACKUP_TIMEZONE}</string>
</dict>
</plist>

Load with: launchctl load ~/Library/LaunchAgents/com.glorng.db-maintenance.plist

Also install a second LaunchAgent for --check-stale (e.g. noon) if not using cron.
EOF
