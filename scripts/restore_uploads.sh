#!/usr/bin/env bash
# Restore the uploads volume from a tar.gz archive produced by backup_uploads.sh.
# Usage: ./restore_uploads.sh <archive.tar.gz>
set -euo pipefail

UPLOAD_DIR="${UPLOAD_DIR:-/var/app/financial-cashflow/uploads}"
ARCHIVE="${1:-}"

if [ -z "$ARCHIVE" ]; then
  echo "Usage: $0 <archive.tar.gz>" >&2
  exit 1
fi
if [ ! -f "$ARCHIVE" ]; then
  echo "Archive not found: $ARCHIVE" >&2
  exit 1
fi

mkdir -p "$(dirname "$UPLOAD_DIR")"
tar -xzf "$ARCHIVE" -C "$(dirname "$UPLOAD_DIR")"
echo "Restored uploads from $ARCHIVE to $UPLOAD_DIR"