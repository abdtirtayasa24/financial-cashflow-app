from contextlib import suppress
from typing import Any, NoReturn

from supabase import Client

from app.core.config import Settings, get_settings
from app.core.errors import AppError
from app.core.models import CurrentUser, Role
from app.modules.app_settings.repository import AppSettingRepository
from app.modules.attachments import storage
from app.modules.attachments.repository import AttachmentRepository
from app.modules.notifications.service import NotificationService
from app.modules.transactions.repository import Rows, TransactionRepository
from app.modules.transactions.schemas import (
    TransactionCreate,
    TransactionOut,
    TransactionUpdate,
)

EDITABLE_FIELDS = (
    "transaction_date",
    "direction",
    "amount",
    "cash_account_id",
    "department_id",
    "category_id",
    "payment_method_id",
    "counterparty_name",
    "reference_no",
    "description",
)


def editable_snapshot(tx: dict[str, Any]) -> dict[str, Any]:
    """Extract a snapshot of editable fields from a transaction dict.

    Used by TransactionService and RecurringGeneratorService to capture
    audit-log old/new values.
    """
    return {f: tx.get(f) for f in EDITABLE_FIELDS}

_MUTABLE_STATUSES = {"DRAFT", "REJECTED"}
# Roles allowed read access to transactions (System Admin is read-only here;
# see CONTEXT.md "Roles & Authorization"). Mutation is gated separately.
_VIEW_ROLES = {
    Role.FINANCE_ADMIN,
    Role.MANAGEMENT,
    Role.SYSTEM_ADMIN,
}
_CREATE_ROLES = {Role.EMPLOYEE, Role.FINANCE_ADMIN}
DEFAULT_LIST_LIMIT = 50
MAX_LIST_LIMIT = 200


class TransactionService:
    def __init__(self, db: Client, settings: Settings | None = None) -> None:
        self.db = db
        self.settings = settings or get_settings()
        self.repo = TransactionRepository(db)
        self.attachments = AttachmentRepository(db)
        self.settings_repo = AppSettingRepository(db)

    # ── authorization helpers ──────────────────────────────────
    def _can_view(self, tx: dict[str, Any], user: CurrentUser) -> bool:
        # FINANCE_ADMIN, MANAGEMENT and SYSTEM_ADMIN see all transactions.
        # SYSTEM_ADMIN is strictly read-only for transactions (cannot mutate).
        if user.role in _VIEW_ROLES:
            return True
        if user.role == Role.EMPLOYEE:
            return bool(tx["created_by"] == user.id)
        if user.role == Role.DEPARTMENT_MANAGER:
            return bool(tx["department_id"] == user.department_id)
        return False

    def _can_mutate(self, tx: dict[str, Any], user: CurrentUser) -> bool:
        if tx["status"] not in _MUTABLE_STATUSES:
            return False
        if user.role == Role.FINANCE_ADMIN:
            return True
        if user.role == Role.EMPLOYEE:
            return bool(tx["created_by"] == user.id)
        return False

    def _require_view(self, tx: dict[str, Any], user: CurrentUser) -> None:
        if not self._can_view(tx, user):
            raise AppError("Transaction not found", 404)

    def _require_mutate(self, tx: dict[str, Any], user: CurrentUser) -> None:
        if user.role not in _CREATE_ROLES:
            raise AppError("forbidden", 403)
        if not self._can_mutate(tx, user):
            if tx["status"] not in _MUTABLE_STATUSES:
                raise AppError(
                    "Only DRAFT and REJECTED transactions can be edited", 409
                )
            raise AppError("forbidden", 403)

    def _require_finance_admin(self, user: CurrentUser) -> None:
        # Approve / reject / void are Finance Admin only. Enforced in the
        # service layer (router also authenticates via get_current_user).
        if user.role != Role.FINANCE_ADMIN:
            raise AppError("forbidden", 403)

    def _require_status(self, tx: dict[str, Any], expected: str) -> None:
        if tx["status"] != expected:
            raise AppError(
                f"Transaction must be {expected} to perform this action", 409
            )

    def _status_conflict_or_not_found(
        self, transaction_id: str, expected: str
    ) -> NoReturn:
        if self.repo.get(transaction_id):
            raise AppError(
                f"Transaction must be {expected} to perform this action", 409
            )
        raise AppError("Transaction not found", 404)

    def _scope_filters(self, user: CurrentUser) -> dict[str, Any]:
        if user.role == Role.EMPLOYEE:
            return {"created_by": user.id}
        if user.role == Role.DEPARTMENT_MANAGER:
            if not user.department_id:
                # A manager without a department cannot see any transactions.
                # Raising prevents the list query from running unscoped.
                raise AppError("forbidden", 403)
            return {"department_id": user.department_id}
        return {}

    # ── transaction number ─────────────────────────────────────
    # next_transaction_no is now on the repository — no duplication.

    # ── attachment threshold ───────────────────────────────────
    def _setting(self, key: str, default: str) -> str:
        row = self.settings_repo.get_by_key(key)
        return row["value"] if row else default

    def _attachment_threshold(self) -> tuple[bool, float]:
        enabled = self._setting("attachment_threshold_enabled", "true").lower() == "true"
        try:
            amount = float(self._setting("attachment_threshold_amount", "5000000"))
        except (TypeError, ValueError):
            amount = 5000000.0
        return enabled, amount

    def _enforce_attachment_threshold(self, tx: dict[str, Any]) -> None:
        enabled, threshold = self._attachment_threshold()
        if not enabled:
            return
        if tx["amount"] < threshold:
            return
        count = len(self.attachments.list_for_transaction(tx["id"]))
        if count == 0:
            raise AppError(
                f"Attachments are required for transactions of "
                f"{int(threshold):,} IDR or above.",
                422,
            )

    # ── audit logging ──────────────────────────────────────────
    def _editable_snapshot(self, tx: dict[str, Any]) -> dict[str, Any]:
        return editable_snapshot(tx)

    def _audit(
        self,
        transaction_id: str,
        actor: CurrentUser,
        action: str,
        *,
        old_value: dict[str, Any] | None = None,
        new_value: dict[str, Any] | None = None,
        reason: str | None = None,
    ) -> None:
        self.repo.audit(
            transaction_id,
            actor.id,
            action,
            old_value=old_value,
            new_value=new_value,
            reason=reason,
        )

    # ── operations ─────────────────────────────────────────────
    def list(
        self,
        filters: dict[str, Any],
        user: CurrentUser,
        *,
        limit: int = DEFAULT_LIST_LIMIT,
        offset: int = 0,
    ) -> list[TransactionOut]:
        # Role scope is applied last so it cannot be overridden by client filters
        # (e.g. an Employee cannot bypass `created_by` via a query parameter).
        merged = {**filters, **self._scope_filters(user)}
        rows = self.repo.list(merged, limit=limit, offset=offset)
        return [TransactionOut(**r) for r in rows]

    def get(self, transaction_id: str, user: CurrentUser) -> TransactionOut:
        tx = self.repo.get(transaction_id)
        if not tx:
            raise AppError("Transaction not found", 404)
        self._require_view(tx, user)
        return TransactionOut(**tx)

    def get_raw_for_view(self, transaction_id: str, user: CurrentUser) -> dict[str, Any]:
        tx = self.repo.get(transaction_id)
        if not tx:
            raise AppError("Transaction not found", 404)
        self._require_view(tx, user)
        return tx

    def get_raw_for_mutation(
        self, transaction_id: str, user: CurrentUser
    ) -> dict[str, Any]:
        tx = self.repo.get(transaction_id)
        if not tx:
            raise AppError("Transaction not found", 404)
        self._require_mutate(tx, user)
        return tx

    def create(self, data: TransactionCreate, user: CurrentUser) -> TransactionOut:
        if user.role not in _CREATE_ROLES:
            raise AppError("forbidden", 403)
        if user.role == Role.EMPLOYEE:
            if not user.department_id:
                raise AppError("Employee has no department assigned", 422)
            if data.department_id != user.department_id:
                raise AppError(
                    "Employees can only create transactions for their own department",
                    403,
                )

        transaction_no = self.repo.next_transaction_no(
            data.direction.value, data.transaction_date
        )
        payload: dict[str, Any] = {
            "transaction_no": transaction_no,
            "transaction_date": data.transaction_date,
            "direction": data.direction.value,
            "amount": data.amount,
            "currency": "IDR",
            "exchange_rate": 1.0,
            "base_amount": data.amount,
            "cash_account_id": data.cash_account_id,
            "department_id": data.department_id,
            "category_id": data.category_id,
            "payment_method_id": data.payment_method_id,
            "counterparty_name": data.counterparty_name,
            "reference_no": data.reference_no,
            "description": data.description,
            "status": "DRAFT",
            "created_by": user.id,
        }
        row = self.repo.insert(payload)
        out = TransactionOut(**row)
        self._audit(
            out.id,
            user,
            "CREATE",
            new_value=self._editable_snapshot(row),
        )
        return out

    def update(
        self, transaction_id: str, data: TransactionUpdate, user: CurrentUser
    ) -> TransactionOut:
        tx = self.get_raw_for_mutation(transaction_id, user)
        payload = data.model_dump(exclude_unset=True)
        # Payment method stays required even on partial update if provided empty.
        if "payment_method_id" in payload and not payload["payment_method_id"]:
            raise AppError("Payment method is required", 422)
        if not payload:
            raise AppError("No fields to update", 422)
        # Recompute base_amount if amount changes (MVP: IDR, rate 1).
        if "amount" in payload:
            payload["base_amount"] = payload["amount"]
        # transaction_no encodes direction + year-month, so it must be
        # regenerated when either changes (system-managed, not client-supplied).
        if "direction" in payload or "transaction_date" in payload:
            new_direction = str(payload.get("direction", tx["direction"]))
            new_date = payload.get("transaction_date", tx["transaction_date"])
            payload["direction"] = new_direction
            payload["transaction_no"] = self.repo.next_transaction_no(
                new_direction, new_date
            )

        old_snapshot = self._editable_snapshot(tx)
        row = self.repo.update(transaction_id, payload)
        if not row:
            raise AppError("Transaction not found", 404)
        new_snapshot = self._editable_snapshot(row)
        self._audit(
            transaction_id,
            user,
            "UPDATE",
            old_value=old_snapshot,
            new_value=new_snapshot,
        )
        return TransactionOut(**row)

    def submit(self, transaction_id: str, user: CurrentUser) -> TransactionOut:
        tx = self.get_raw_for_mutation(transaction_id, user)
        self._enforce_attachment_threshold(tx)
        update_payload: dict[str, Any] = {
            "status": "SUBMITTED",
            "submitted_at": _now_iso(),
        }
        new_value: dict[str, Any] = {
            "status": "SUBMITTED",
            "submitted_at": None,  # filled from the returned row below
        }
        # Resubmitting a rejected transaction clears the prior review metadata;
        # the history is preserved in the audit trail.
        if tx["status"] == "REJECTED":
            update_payload["rejection_reason"] = None
            update_payload["reviewed_by"] = None
            update_payload["reviewed_at"] = None
            new_value["rejection_reason"] = None
            new_value["reviewed_by"] = None
            new_value["reviewed_at"] = None
        row = self.repo.update(transaction_id, update_payload)
        if not row:
            raise AppError("Transaction not found", 404)
        new_value["submitted_at"] = row["submitted_at"]
        self._audit(
            transaction_id,
            user,
            "SUBMIT",
            old_value={"status": tx["status"]},
            new_value=new_value,
        )
        # Notifications are best-effort after the financial status change
        # and mandatory audit log are persisted.
        with suppress(Exception):
            NotificationService(self.db).notify_pending_approval(row)
        return TransactionOut(**row)

    def approve(self, transaction_id: str, user: CurrentUser) -> TransactionOut:
        tx = self.repo.get(transaction_id)
        if not tx:
            raise AppError("Transaction not found", 404)
        self._require_finance_admin(user)
        self._require_status(tx, "SUBMITTED")
        row = self.repo.update_if_status(
            transaction_id,
            "SUBMITTED",
            {
                "status": "APPROVED",
                "reviewed_by": user.id,
                "reviewed_at": _now_iso(),
            },
        )
        if not row:
            self._status_conflict_or_not_found(transaction_id, "SUBMITTED")
        self._audit(
            transaction_id,
            user,
            "APPROVE",
            old_value={"status": tx["status"]},
            new_value={
                "status": "APPROVED",
                "reviewed_by": row["reviewed_by"],
                "reviewed_at": row["reviewed_at"],
            },
        )
        return TransactionOut(**row)

    def reject(
        self, transaction_id: str, reason: str, user: CurrentUser
    ) -> TransactionOut:
        tx = self.repo.get(transaction_id)
        if not tx:
            raise AppError("Transaction not found", 404)
        self._require_finance_admin(user)
        self._require_status(tx, "SUBMITTED")
        row = self.repo.update_if_status(
            transaction_id,
            "SUBMITTED",
            {
                "status": "REJECTED",
                "reviewed_by": user.id,
                "reviewed_at": _now_iso(),
                "rejection_reason": reason,
            },
        )
        if not row:
            self._status_conflict_or_not_found(transaction_id, "SUBMITTED")
        self._audit(
            transaction_id,
            user,
            "REJECT",
            old_value={"status": tx["status"]},
            new_value={
                "status": "REJECTED",
                "reviewed_by": row["reviewed_by"],
                "reviewed_at": row["reviewed_at"],
                "rejection_reason": reason,
            },
            reason=reason,
        )
        return TransactionOut(**row)

    def void(
        self, transaction_id: str, reason: str, user: CurrentUser
    ) -> TransactionOut:
        tx = self.repo.get(transaction_id)
        if not tx:
            raise AppError("Transaction not found", 404)
        self._require_finance_admin(user)
        self._require_status(tx, "APPROVED")
        row = self.repo.update_if_status(
            transaction_id,
            "APPROVED",
            {"status": "VOIDED", "void_reason": reason},
        )
        if not row:
            self._status_conflict_or_not_found(transaction_id, "APPROVED")
        self._audit(
            transaction_id,
            user,
            "VOID",
            old_value={"status": tx["status"]},
            new_value={"status": "VOIDED", "void_reason": reason},
            reason=reason,
        )
        return TransactionOut(**row)

    def delete(self, transaction_id: str, user: CurrentUser) -> None:
        tx = self.get_raw_for_mutation(transaction_id, user)

        # Final audit entry BEFORE deletion (so the trail records the act).
        self._audit(
            transaction_id,
            user,
            "DELETE",
            old_value=self._editable_snapshot(tx),
        )

        # Remove attachment files + metadata.
        for att in self.attachments.list_for_transaction(transaction_id):
            storage.delete_file(att["relative_path"], self.settings)
        self.attachments.delete_for_transaction(transaction_id)

        # Remove audit logs, then the transaction itself.
        self.repo.delete_audit_logs(transaction_id)
        self.repo.delete(transaction_id)

    def audit_logs(
        self, transaction_id: str, user: CurrentUser
    ) -> Rows:
        tx = self.get_raw_for_view(transaction_id, user)
        logs = self.repo.list_audit_logs(tx["id"])
        names = self.repo.user_names([lg["actor_user_id"] for lg in logs])
        for lg in logs:
            lg["actor_name"] = names.get(lg["actor_user_id"])
        return logs


def _now_iso() -> str:
    from datetime import UTC, datetime

    return datetime.now(UTC).isoformat()