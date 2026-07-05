#!/usr/bin/env python3
"""Expired export cleanup cron job.

Deletes files from the exports directory that are older than the configured
retention period (app_settings key 'export_retention_days', default 7 days).
Run at 02:00 daily.

Usage:
    python scripts/cleanup_old_exports.py
"""

import logging
import sys

from app.core.config import get_settings
from app.core.supabase_client import get_supabase_client
from app.cron.export_cleanup import ExportCleanupService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("cleanup_old_exports")


def main() -> int:
    logger.info("Starting expired export cleanup")
    try:
        settings = get_settings()
        db = get_supabase_client()
        service = ExportCleanupService(db, exports_dir=settings.exports_dir)
        deleted = service.run()
        logger.info("Expired export cleanup completed: %d file(s) deleted", deleted)
        return 0
    except Exception:
        logger.exception("Expired export cleanup failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())