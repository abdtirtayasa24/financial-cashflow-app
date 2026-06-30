#!/usr/bin/env bash
# Back up the uploads volume to a timestamped tar.gz archive.
set -euo pipefail

UPLOAD_DIR="${UPLOAD_DIR:-/var/app/financial-cashflow/uploads}"
BACKUP_DIR="${BACKUP_DIR:-/var/backups/financial-cashflow/uploads}"

TS="$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"

tar -czf "$BACKUP_DIR/uploads-$TS.tar.gz" \
  -C "$(dirname "$UPLOAD_DIR")" "$(basename "$UPLOAD_DIR")"

echo "Backup created: $BACKUP_DIR/uploads-$TS.tar.gz"