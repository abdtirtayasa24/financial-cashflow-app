from typing import Any, cast

from supabase import Client

Rows = list[dict[str, Any]]
StrList = list[str]


class TransactionRepository:
    table = "cashflow_transactions"
    audit_table = "transaction_audit_logs"

    def __init__(self, db: Client) -> None:
        self.db = db

    # ── transactions ───────────────────────────────────────────
    def list(
        self,
        filters: dict[str, Any],
        *,
        limit: int = 50,
        offset: int = 0,
    ) -> Rows:
        query = self.db.table(self.table).select("*")
        if filters.get("date_from"):
            query = query.gte("transaction_date", filters["date_from"])
        if filters.get("date_to"):
            query = query.lte("transaction_date", filters["date_to"])
        for col in (
            "department_id",
            "category_id",
            "cash_account_id",
            "status",
            "direction",
            "created_by",
        ):
            value = filters.get(col)
            if value:
                query = query.eq(col, value)
        query = query.order("transaction_date", desc=True).order(
            "transaction_no", desc=True
        )
        query = query.range(offset, offset + limit - 1)
        return cast(list[dict[str, Any]], query.execute().data)

    def get(self, transaction_id: str) -> dict[str, Any] | None:
        resp = (
            self.db.table(self.table)
            .select("*")
            .eq("id", transaction_id)
            .limit(1)
            .execute()
        )
        rows = cast(list[dict[str, Any]], resp.data)
        return rows[0] if rows else None

    def insert(self, payload: dict[str, Any]) -> dict[str, Any]:
        resp = self.db.table(self.table).insert(payload).execute()
        return cast(list[dict[str, Any]], resp.data)[0]

    def update(
        self, transaction_id: str, payload: dict[str, Any]
    ) -> dict[str, Any] | None:
        resp = (
            self.db.table(self.table)
            .update(payload)
            .eq("id", transaction_id)
            .execute()
        )
        rows = cast(list[dict[str, Any]], resp.data)
        return rows[0] if rows else None

    def update_if_status(
        self, transaction_id: str, expected_status: str, payload: dict[str, Any]
    ) -> dict[str, Any] | None:
        resp = (
            self.db.table(self.table)
            .update(payload)
            .eq("id", transaction_id)
            .eq("status", expected_status)
            .execute()
        )
        rows = cast(list[dict[str, Any]], resp.data)
        return rows[0] if rows else None

    def delete(self, transaction_id: str) -> int:
        resp = self.db.table(self.table).delete().eq("id", transaction_id).execute()
        return len(cast(list[dict[str, Any]], resp.data))

    def existing_transaction_nos(self, direction: str) -> StrList:
        """All transaction_no values for a direction (any month)."""
        resp = (
            self.db.table(self.table)
            .select("transaction_no")
            .eq("direction", direction)
            .execute()
        )
        return [r["transaction_no"] for r in cast(Rows, resp.data)]

    # ── audit logs ─────────────────────────────────────────────
    def list_audit_logs(self, transaction_id: str) -> Rows:
        resp = (
            self.db.table(self.audit_table)
            .select("*")
            .eq("transaction_id", transaction_id)
            .order("created_at")
            .execute()
        )
        return cast(Rows, resp.data)

    def insert_audit_log(self, payload: dict[str, Any]) -> None:
        self.db.table(self.audit_table).insert(payload).execute()

    def delete_audit_logs(self, transaction_id: str) -> int:
        resp = (
            self.db.table(self.audit_table)
            .delete()
            .eq("transaction_id", transaction_id)
            .execute()
        )
        return len(cast(Rows, resp.data))

    # ── reference: actor names for audit trail ─────────────────
    def user_names(self, user_ids: StrList) -> dict[str, str]:
        if not user_ids:
            return {}
        resp = (
            self.db.table("user_profiles")
            .select("id,full_name")
            .in_("id", user_ids)
            .execute()
        )
        return {r["id"]: r["full_name"] for r in cast(list[dict[str, Any]], resp.data)}