#!/usr/bin/env python3
"""Daily report snapshot cron job.

Computes report data from APPROVED transactions and stores it in the
report_snapshots table. Run at 01:00 daily.

Usage:
    python scripts/refresh_report_snapshots.py
"""

import logging
import sys
from datetime import date

from app.core.supabase_client import get_supabase_client
from app.cron.report_snapshot import ReportSnapshotService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("refresh_report_snapshots")


def main() -> int:
    today = date.today()
    logger.info("Starting daily report snapshot for %s", today.isoformat())
    try:
        db = get_supabase_client()
        service = ReportSnapshotService(db)
        service.daily_snapshot(today=today)
        logger.info("Daily report snapshot completed successfully")
        return 0
    except Exception:
        logger.exception("Daily report snapshot failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())