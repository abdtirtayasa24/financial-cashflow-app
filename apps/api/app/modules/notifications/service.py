from typing import Any

from supabase import Client

from app.core.errors import AppError
from app.core.models import CurrentUser
from app.modules.notifications.repository import NotificationRepository
from app.modules.notifications.schemas import (
    MarkAllReadOut,
    NotificationOut,
    NotificationType,
    UnreadCountOut,
)

DEFAULT_LIST_LIMIT = 20
MAX_LIST_LIMIT = 100


class NotificationService:
    def __init__(self, db: Client) -> None:
        self.repo = NotificationRepository(db)

    def list(
        self,
        user: CurrentUser,
        *,
        limit: int = DEFAULT_LIST_LIMIT,
        offset: int = 0,
    ) -> list[NotificationOut]:
        rows = self.repo.list_for_user(user.id, limit=limit, offset=offset)
        return [NotificationOut(**row) for row in rows]

    def unread_count(self, user: CurrentUser) -> UnreadCountOut:
        return UnreadCountOut(count=self.repo.unread_count(user.id))

    def mark_read(self, notification_id: str, user: CurrentUser) -> NotificationOut:
        row = self.repo.mark_read(notification_id, user.id)
        if not row:
            raise AppError("Notification not found", 404)
        return NotificationOut(**row)

    def mark_all_read(self, user: CurrentUser) -> MarkAllReadOut:
        return MarkAllReadOut(updated=self.repo.mark_all_read(user.id))

    def notify_pending_approval(self, transaction: dict[str, Any]) -> int:
        transaction_id = str(transaction["id"])
        transaction_no = str(transaction["transaction_no"])
        rows = []
        for user_id in self.repo.active_finance_admin_ids():
            if self.repo.has_unread_for_transaction(
                user_id=user_id,
                notification_type=NotificationType.PENDING_APPROVAL.value,
                transaction_id=transaction_id,
            ):
                continue
            rows.append(
                {
                    "user_id": user_id,
                    "type": NotificationType.PENDING_APPROVAL.value,
                    "title": "Transaction pending approval",
                    "message": (
                        f"Transaction {transaction_no} is awaiting finance review."
                    ),
                    "related_transaction_id": transaction_id,
                    "is_read": False,
                }
            )
        return self.repo.insert_many(rows)

    def notify_recurring_draft_ready(
        self,
        *,
        user_id: str,
        transaction_id: str,
        transaction_no: str,
    ) -> int:
        if self.repo.has_unread_for_transaction(
            user_id=user_id,
            notification_type=NotificationType.RECURRING_DRAFT_READY.value,
            transaction_id=transaction_id,
        ):
            return 0
        return self.repo.insert_many(
            [
                {
                    "user_id": user_id,
                    "type": NotificationType.RECURRING_DRAFT_READY.value,
                    "title": "Recurring draft ready",
                    "message": (
                        f"Recurring transaction {transaction_no} is ready to review."
                    ),
                    "related_transaction_id": transaction_id,
                    "is_read": False,
                }
            ]
        )
