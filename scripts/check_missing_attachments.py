#!/usr/bin/env python3
"""Missing attachment check cron job.

Reads attachment threshold settings from app_settings, queries SUBMITTED
transactions above the threshold, and logs warnings for any that lack
attachments. This job is read-only — it never modifies transaction data.
Run at 04:00 daily.

Usage:
    python scripts/check_missing_attachments.py
"""

import logging
import sys

from app.core.supabase_client import get_supabase_client
from app.cron.attachment_check import AttachmentCheckService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("check_missing_attachments")


def main() -> int:
    logger.info("Starting missing attachment check")
    try:
        db = get_supabase_client()
        service = AttachmentCheckService(db)
        result = service.run()
        logger.info(
            "Missing attachment check completed: %d checked, %d flagged",
            result.checked,
            result.flagged,
        )
        return 0
    except Exception:
        logger.exception("Missing attachment check failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())