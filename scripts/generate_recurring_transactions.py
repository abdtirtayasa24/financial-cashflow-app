#!/usr/bin/env python3
"""Recurring transaction generation cron job.

Queries due recurring_transaction_templates, generates cashflow transactions,
advances next_run_date, and triggers notifications for DRAFT-mode templates.
Run at 05:00 daily.

Usage:
    python scripts/generate_recurring_transactions.py
"""

import logging
import sys
from datetime import date

from app.core.supabase_client import get_supabase_client
from app.cron.recurring_generator import RecurringGeneratorService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("generate_recurring_transactions")


def main() -> int:
    today = date.today()
    logger.info("Starting recurring transaction generation for %s", today.isoformat())
    try:
        db = get_supabase_client()
        service = RecurringGeneratorService(db)
        result = service.run(today=today)
        logger.info(
            "Recurring transaction generation completed: "
            "%d generated, %d skipped, %d errors",
            result.generated,
            result.skipped,
            result.errors,
        )
        if result.errors:
            logger.warning("%d template(s) had errors during generation", result.errors)
        return 0
    except Exception:
        logger.exception("Recurring transaction generation failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())