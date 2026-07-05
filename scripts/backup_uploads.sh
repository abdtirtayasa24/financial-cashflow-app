#!/usr/bin/env bash
# Back up the uploads volume to a timestamped tar.gz archive.
# Retains backups for 30 days — older backups are deleted after each run.
# Run at 03:00 daily.
set -euo pipefail

UPLOAD_DIR="${UPLOAD_DIR:-/var/app/financial-cashflow/uploads}"
BACKUP_DIR="${BACKUP_DIR:-/var/backups/financial-cashflow/uploads}"
RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-30}"

TS="$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"

tar -czf "$BACKUP_DIR/uploads-$TS.tar.gz" \
  -C "$(dirname "$UPLOAD_DIR")" "$(basename "$UPLOAD_DIR")"

echo "Backup created: $BACKUP_DIR/uploads-$TS.tar.gz"

# Delete backups older than RETENTION_DAYS.
find "$BACKUP_DIR" -name 'uploads-*.tar.gz' -type f \
  -mtime +"$RETENTION_DAYS" -delete

echo "Retention: removed backups older than $RETENTION_DAYS days"