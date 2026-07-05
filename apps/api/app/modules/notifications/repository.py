from typing import Any, cast

from supabase import Client

Rows = list[dict[str, Any]]


def _coerce_count(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


class NotificationRepository:
    table = "notifications"

    def __init__(self, db: Client) -> None:
        self.db = db

    def list_for_user(
        self, user_id: str, *, limit: int = 20, offset: int = 0
    ) -> Rows:
        resp = (
            self.db.table(self.table)
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .range(offset, offset + limit - 1)
            .execute()
        )
        return cast(Rows, resp.data)

    def unread_count(self, user_id: str) -> int:
        resp = self.db.rpc(
            "notification_unread_count", {"p_user_id": user_id}
        ).execute()
        data = resp.data
        if isinstance(data, int):
            return data
        if isinstance(data, list):
            if not data:
                return 0
            first = data[0]
            if isinstance(first, dict):
                value = first.get("notification_unread_count", first.get("count", 0))
                return _coerce_count(value)
            return _coerce_count(first)
        return _coerce_count(data)

    def mark_read(
        self, notification_id: str, user_id: str
    ) -> dict[str, Any] | None:
        resp = (
            self.db.table(self.table)
            .update({"is_read": True})
            .eq("id", notification_id)
            .eq("user_id", user_id)
            .execute()
        )
        rows = cast(Rows, resp.data)
        return rows[0] if rows else None

    def mark_all_read(self, user_id: str) -> int:
        resp = (
            self.db.table(self.table)
            .update({"is_read": True})
            .eq("user_id", user_id)
            .eq("is_read", False)
            .execute()
        )
        return len(cast(Rows, resp.data))

    def active_finance_admin_ids(self) -> list[str]:
        resp = (
            self.db.table("user_profiles")
            .select("id")
            .eq("role", "FINANCE_ADMIN")
            .eq("status", "ACTIVE")
            .execute()
        )
        return [row["id"] for row in cast(Rows, resp.data)]

    def has_unread_for_transaction(
        self, *, user_id: str, notification_type: str, transaction_id: str
    ) -> bool:
        resp = (
            self.db.table(self.table)
            .select("id")
            .eq("user_id", user_id)
            .eq("type", notification_type)
            .eq("related_transaction_id", transaction_id)
            .eq("is_read", False)
            .limit(1)
            .execute()
        )
        return bool(cast(Rows, resp.data))

    def insert_many(self, rows: Rows) -> int:
        if not rows:
            return 0
        resp = self.db.table(self.table).insert(rows).execute()
        return len(cast(Rows, resp.data))
