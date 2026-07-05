"""Recurring transaction generation cron job service.

Queries due recurring_transaction_templates, creates cashflow transactions
from each template, advances next_run_date, and triggers notifications for
DRAFT-mode templates. Designed to be idempotent: running the job twice on the
same day must not create duplicate transactions.
"""

from __future__ import annotations

from contextlib import suppress
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any, cast

from supabase import Client

from app.modules.notifications.service import NotificationService
from app.modules.transactions.repository import TransactionRepository
from app.modules.transactions.service import editable_snapshot


@dataclass
class GenerationResult:
    generated: int = 0
    skipped: int = 0
    errors: int = 0


class RecurringGeneratorService:
    def __init__(self, db: Client) -> None:
        self.db = db
        self.repo = TransactionRepository(db)

    def run(self, today: date | None = None) -> GenerationResult:
        today = today or date.today()
        result = GenerationResult()
        templates = self._due_templates(today)
        for tpl in templates:
            try:
                tx_date = str(tpl["next_run_date"])
                if self._already_generated(tpl["id"], tx_date):
                    result.skipped += 1
                    continue
                self._generate_from_template(tpl)
                result.generated += 1
            except Exception:
                result.errors += 1
        return result

    # ── queries ───────────────────────────────────────────────
    def _due_templates(self, today: date) -> list[dict[str, Any]]:
        """Active templates whose next_run_date is due.

        Pushes down the is_active and next_run_date <= today filters to the
        database. The end_date filter (NULL OR >= today) is applied in Python
        because the Supabase query builder doesn't support OR conditions.
        """
        today_str = today.isoformat()
        rows = cast(
            list[dict[str, Any]],
            self.db.table("recurring_transaction_templates")
            .select("*")
            .eq("is_active", True)
            .lte("next_run_date", today_str)
            .execute()
            .data,
        )
        return [
            row
            for row in rows
            if row.get("end_date") is None
            or str(row["end_date"]) >= today_str
        ]

    def _already_generated(self, template_id: str, transaction_date: str) -> bool:
        """Check if a transaction was already generated for this template on the
        given transaction_date (which is the template's next_run_date, not
        necessarily today)."""
        rows = cast(
            list[dict[str, Any]],
            self.db.table("cashflow_transactions")
            .select("id")
            .eq("recurring_template_id", template_id)
            .eq("transaction_date", transaction_date)
            .limit(1)
            .execute()
            .data,
        )
        return bool(rows)

    # ── transaction creation ──────────────────────────────────
    def _generate_from_template(self, tpl: dict[str, Any]) -> None:
        direction = tpl["direction"]
        transaction_date = str(tpl["next_run_date"])
        transaction_no = self.repo.next_transaction_no(direction, transaction_date)

        status = (
            "SUBMITTED" if tpl["submission_mode"] == "AUTO_SUBMIT" else "DRAFT"
        )
        submitted_at = _now_iso() if status == "SUBMITTED" else None

        payload: dict[str, Any] = {
            "transaction_no": transaction_no,
            "transaction_date": transaction_date,
            "direction": direction,
            "amount": tpl["amount"],
            "currency": tpl.get("currency", "IDR"),
            "exchange_rate": 1.0,
            "base_amount": tpl["amount"],
            "cash_account_id": tpl["cash_account_id"],
            "department_id": tpl["department_id"],
            "category_id": tpl["category_id"],
            "payment_method_id": tpl.get("payment_method_id"),
            "counterparty_name": tpl.get("counterparty_name"),
            "reference_no": tpl.get("reference_no"),
            "description": tpl.get("description"),
            "status": status,
            "created_by": tpl["created_by"],
            "recurring_template_id": tpl["id"],
        }
        if submitted_at:
            payload["submitted_at"] = submitted_at

        row = self.repo.insert(payload)

        # Audit log
        self.repo.audit(
            row["id"],
            tpl["created_by"],
            "CREATE",
            new_value=editable_snapshot(row),
        )
        if status == "SUBMITTED":
            self.repo.audit(
                row["id"],
                tpl["created_by"],
                "SUBMIT",
                old_value={"status": "DRAFT"},
                new_value={"status": "SUBMITTED"},
            )
            # Notify finance admins about the new submitted transaction.
            with suppress(Exception):
                NotificationService(self.db).notify_pending_approval(row)
        else:
            # DRAFT mode: notify the template creator.
            with suppress(Exception):
                NotificationService(self.db).notify_recurring_draft_ready(
                    user_id=tpl["created_by"],
                    transaction_id=row["id"],
                    transaction_no=row["transaction_no"],
                )

        # Advance next_run_date
        self._advance_template(tpl)

    def _advance_template(self, tpl: dict[str, Any]) -> None:
        new_date = _advance_date(
            tpl["next_run_date"], tpl["frequency"], tpl["interval"]
        )
        update_payload: dict[str, Any] = {"next_run_date": new_date.isoformat()}
        end_date_raw = tpl.get("end_date")
        if end_date_raw:
            end_date = _parse_date(end_date_raw)
            if new_date > end_date:
                update_payload["is_active"] = False
        self.db.table("recurring_transaction_templates").update(
            update_payload
        ).eq("id", tpl["id"]).execute()

    # ── helpers ───────────────────────────────────────────────
    # _audit and _snapshot are no longer duplicated here — the repo's
    # audit() method and the shared editable_snapshot() function are used
    # directly from _generate_from_template above.


def _advance_date(current: str, frequency: str, interval: int) -> date:
    """Advance a date string by interval periods of the given frequency."""
    base = _parse_date(current)
    if frequency == "DAILY":
        return base + timedelta(days=interval)
    if frequency == "WEEKLY":
        return base + timedelta(weeks=interval)
    if frequency == "MONTHLY":
        month = base.month - 1 + interval
        year = base.year + month // 12
        month = month % 12 + 1
        day = min(base.day, _days_in_month(year, month))
        return date(year, month, day)
    raise ValueError(f"Unknown frequency: {frequency}")


def _parse_date(value: Any) -> date:
    """Parse a date from a string or date object."""
    if isinstance(value, date):
        return value
    from datetime import datetime
    return datetime.strptime(str(value), "%Y-%m-%d").date()


def _days_in_month(year: int, month: int) -> int:
    next_month = date(year + 1, 1, 1) if month == 12 else date(year, month + 1, 1)
    return (next_month - timedelta(days=1)).day


def _now_iso() -> str:
    from datetime import UTC, datetime

    return datetime.now(UTC).isoformat()