#!/usr/bin/env bash
# Install a daily 4:20 AM cron job for db_maintenance.sh (Europe/Warsaw by default).
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
LOG_FILE="${BACKUP_CRON_LOG:-$root/logs/backup.log}"
MAINTENANCE_SCRIPT="$root/scripts/db_maintenance.sh"

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
  printf '%s\n' "${CRON_SCHEDULE} cd ${root} && ${MAINTENANCE_SCRIPT} >> ${LOG_FILE} 2>&1"
  printf '%s\n' "# portfolio-glorng-db-maintenance-end"
} | crontab -

cat <<EOF
Installed daily DB maintenance cron job.

  Schedule : ${CRON_SCHEDULE} (${BACKUP_TIMEZONE})
  Script   : ${MAINTENANCE_SCRIPT}
  Log      : ${LOG_FILE}

Verify with: crontab -l | grep portfolio-glorng

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
EOF
