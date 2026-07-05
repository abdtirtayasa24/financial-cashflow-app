"""Expired export cleanup cron job service.

Deletes files from the exports directory that are older than the configured
retention period (read from app_settings key `export_retention_days`,
default 7). Safe to run multiple times — deleting already-deleted files is
a no-op.
"""

from __future__ import annotations

import time
from pathlib import Path

from supabase import Client

from app.modules.app_settings.repository import AppSettingRepository

DEFAULT_RETENTION_DAYS = 7


class ExportCleanupService:
    def __init__(self, db: Client, *, exports_dir: str) -> None:
        self.db = db
        self.exports_dir = Path(exports_dir)
        self.settings_repo = AppSettingRepository(db)

    def run(self) -> int:
        """Delete expired files from the exports directory.

        Returns the count of files deleted.
        """
        if not self.exports_dir.is_dir():
            return 0

        retention_days = self._retention_days()
        cutoff = time.time() - (retention_days * 86400)
        deleted = 0

        for entry in self.exports_dir.iterdir():
            if not entry.is_file():
                continue
            try:
                mtime = entry.stat().st_mtime
            except OSError:
                continue
            if mtime < cutoff:
                try:
                    entry.unlink()
                    deleted += 1
                except OSError:
                    pass

        return deleted

    def _retention_days(self) -> int:
        row = self.settings_repo.get_by_key("export_retention_days")
        if not row:
            return DEFAULT_RETENTION_DAYS
        try:
            return int(row["value"])
        except (TypeError, ValueError):
            return DEFAULT_RETENTION_DAYS