"""Report snapshot cron job service.

Computes report data (summary, monthly trend, category/department breakdown,
cash account balances) from APPROVED transactions and stores the result in
the report_snapshots table. Designed to be idempotent: running the job twice
for the same date range upserts rather than duplicates.
"""

from __future__ import annotations

import json
from datetime import date, timedelta
from typing import Any, cast

from supabase import Client

from app.core.models import CurrentUser, Role, UserStatus
from app.modules.reports.schemas import ReportFilters
from app.modules.reports.service import ReportService

_SYSTEM_USER = CurrentUser(
    id="cron-snapshot",
    role=Role.FINANCE_ADMIN,
    full_name="Cron Snapshot",
    status=UserStatus.ACTIVE,
)


class ReportSnapshotService:
    def __init__(self, db: Client) -> None:
        self.db = db
        self.reports = ReportService(db)

    def daily_snapshot(self, today: date | None = None) -> None:
        today = today or date.today()
        # Daily snapshot captures the full report state as of today
        # (no date-range filter on the report data itself).
        self._store_snapshot(
            report_type="daily_summary",
            date_from=today,
            date_to=today,
            filters=ReportFilters(),
        )

    def monthly_snapshot(self, today: date | None = None) -> None:
        today = today or date.today()
        first_of_month = today.replace(day=1)
        prev_month_last = first_of_month - _one_day()
        prev_month_first = prev_month_last.replace(day=1)
        # Monthly snapshot is filtered to the previous calendar month.
        self._store_snapshot(
            report_type="monthly_summary",
            date_from=prev_month_first,
            date_to=prev_month_last,
            filters=ReportFilters(
                date_from=prev_month_first.isoformat(),
                date_to=prev_month_last.isoformat(),
            ),
        )

    # ── internals ─────────────────────────────────────────────
    def _store_snapshot(
        self,
        *,
        report_type: str,
        date_from: date,
        date_to: date,
        filters: ReportFilters,
    ) -> None:
        payload = self._compute_payload(filters)
        existing = self._find_existing(report_type, date_from, date_to)
        if existing:
            self.db.table("report_snapshots").update(
                {"result": json.loads(json.dumps(payload))}
            ).eq("id", existing["id"]).execute()
        else:
            self.db.table("report_snapshots").insert(
                {
                    "report_type": report_type,
                    "date_from": date_from.isoformat(),
                    "date_to": date_to.isoformat(),
                    "filters": None,
                    "result": json.loads(json.dumps(payload)),
                    "generated_by": None,
                }
            ).execute()

    def _compute_payload(self, filters: ReportFilters) -> dict[str, Any]:
        summary = self.reports.summary(filters, _SYSTEM_USER)
        monthly = self.reports.monthly_trend(filters, _SYSTEM_USER)
        by_category = self.reports.by_category(filters, _SYSTEM_USER)
        by_department = self.reports.by_department(filters, _SYSTEM_USER)
        cash_balances = self.reports.cash_account_balances(filters, _SYSTEM_USER)
        return {
            "summary": summary.model_dump(by_alias=True),
            "monthly_trend": [m.model_dump() for m in monthly],
            "by_category": [c.model_dump() for c in by_category],
            "by_department": [d.model_dump() for d in by_department],
            "cash_account_balances": [b.model_dump() for b in cash_balances],
        }

    def _find_existing(
        self, report_type: str, date_from: date, date_to: date
    ) -> dict[str, Any] | None:
        rows = cast(
            list[dict[str, Any]],
            self.db.table("report_snapshots")
            .select("id")
            .eq("report_type", report_type)
            .eq("date_from", date_from.isoformat())
            .eq("date_to", date_to.isoformat())
            .limit(1)
            .execute()
            .data,
        )
        return rows[0] if rows else None


def _one_day() -> timedelta:
    return timedelta(days=1)