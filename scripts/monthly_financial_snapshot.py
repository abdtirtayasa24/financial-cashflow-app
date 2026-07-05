#!/usr/bin/env python3
"""Monthly financial snapshot cron job.

Computes and stores a comprehensive monthly snapshot covering the previous
calendar month. Run at 01:30 on the first day of each month.

Usage:
    python scripts/monthly_financial_snapshot.py
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
logger = logging.getLogger("monthly_financial_snapshot")


def main() -> int:
    today = date.today()
    logger.info("Starting monthly financial snapshot for %s", today.isoformat())
    try:
        db = get_supabase_client()
        service = ReportSnapshotService(db)
        service.monthly_snapshot(today=today)
        logger.info("Monthly financial snapshot completed successfully")
        return 0
    except Exception:
        logger.exception("Monthly financial snapshot failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())