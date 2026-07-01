from typing import Any, cast

from supabase import Client


class AttachmentRepository:
    """Metadata access for transaction_attachments.

    File bytes live on VPS local storage (see ``attachments.storage``); only
    metadata is stored in PostgreSQL.
    """

    table = "transaction_attachments"

    def __init__(self, db: Client) -> None:
        self.db = db

    def list_for_transaction(self, transaction_id: str) -> list[dict[str, Any]]:
        resp = (
            self.db.table(self.table)
            .select("*")
            .eq("transaction_id", transaction_id)
            .order("uploaded_at")
            .execute()
        )
        return cast(list[dict[str, Any]], resp.data)

    def get(self, attachment_id: str) -> dict[str, Any] | None:
        resp = (
            self.db.table(self.table)
            .select("*")
            .eq("id", attachment_id)
            .limit(1)
            .execute()
        )
        rows = cast(list[dict[str, Any]], resp.data)
        return rows[0] if rows else None

    def insert(self, payload: dict[str, Any]) -> dict[str, Any]:
        resp = self.db.table(self.table).insert(payload).execute()
        return cast(list[dict[str, Any]], resp.data)[0]

    def delete(self, attachment_id: str) -> dict[str, Any] | None:
        resp = (
            self.db.table(self.table)
            .delete()
            .eq("id", attachment_id)
            .execute()
        )
        rows = cast(list[dict[str, Any]], resp.data)
        return rows[0] if rows else None

    def delete_for_transaction(self, transaction_id: str) -> list[dict[str, Any]]:
        resp = (
            self.db.table(self.table)
            .delete()
            .eq("transaction_id", transaction_id)
            .execute()
        )
        return cast(list[dict[str, Any]], resp.data)