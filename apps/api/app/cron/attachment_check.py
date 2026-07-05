"""Missing attachment check cron job service.

Reads attachment threshold settings from app_settings, queries SUBMITTED
transactions above the threshold, and logs warnings for any that lack
attachments. This job is strictly read-only — it never modifies transaction
data. Re-running the job produces the same result without side effects.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, cast

from supabase import Client

from app.modules.app_settings.repository import AppSettingRepository

logger = logging.getLogger(__name__)


@dataclass
class AttachmentCheckResult:
    checked: int = 0
    flagged: int = 0


class AttachmentCheckService:
    def __init__(self, db: Client) -> None:
        self.db = db
        self.settings_repo = AppSettingRepository(db)

    def run(self) -> AttachmentCheckResult:
        enabled, threshold = self._threshold()
        if not enabled:
            return AttachmentCheckResult()

        submitted = self._submitted_transactions()
        result = AttachmentCheckResult(checked=len(submitted))
        for tx in submitted:
            if tx.get("amount", 0) < threshold:
                continue
            if not self._has_attachments(tx["id"]):
                result.flagged += 1
                logger.warning(
                    "Missing attachment: transaction %s (%s) "
                    "amount %s is above threshold %s",
                    tx["transaction_no"],
                    tx["id"],
                    tx["amount"],
                    threshold,
                )
        return result

    # ── internals ─────────────────────────────────────────────
    def _threshold(self) -> tuple[bool, float]:
        enabled_row = self.settings_repo.get_by_key("attachment_threshold_enabled")
        enabled = (enabled_row or {}).get("value", "true").lower() == "true"
        amount_row = self.settings_repo.get_by_key("attachment_threshold_amount")
        try:
            amount = float((amount_row or {}).get("value", "5000000"))
        except (TypeError, ValueError):
            amount = 5_000_000.0
        return enabled, amount

    def _submitted_transactions(self) -> list[dict[str, Any]]:
        return cast(
            list[dict[str, Any]],
            self.db.table("cashflow_transactions")
            .select("*")
            .eq("status", "SUBMITTED")
            .execute()
            .data,
        )

    def _has_attachments(self, transaction_id: str) -> bool:
        rows = cast(
            list[dict[str, Any]],
            self.db.table("transaction_attachments")
            .select("id")
            .eq("transaction_id", transaction_id)
            .limit(1)
            .execute()
            .data,
        )
        return bool(rows)