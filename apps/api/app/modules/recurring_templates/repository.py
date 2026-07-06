from typing import Any, cast

from supabase import Client

Rows = list[dict[str, Any]]


class RecurringTemplateRepository:
    table = "recurring_transaction_templates"

    def __init__(self, db: Client) -> None:
        self.db = db

    def list(self, filters: dict[str, Any]) -> Rows:
        query = self.db.table(self.table).select("*")
        for col in ("department_id", "created_by", "is_active"):
            if col in filters and filters[col] is not None:
                query = query.eq(col, filters[col])
        return cast(Rows, query.order("next_run_date").execute().data)

    def get(self, template_id: str) -> dict[str, Any] | None:
        rows = cast(
            Rows,
            self.db.table(self.table)
            .select("*")
            .eq("id", template_id)
            .limit(1)
            .execute()
            .data,
        )
        return rows[0] if rows else None

    def create(self, payload: dict[str, Any]) -> dict[str, Any]:
        rows = cast(Rows, self.db.table(self.table).insert(payload).execute().data)
        return rows[0]

    def update(self, template_id: str, payload: dict[str, Any]) -> dict[str, Any] | None:
        rows = cast(
            Rows,
            self.db.table(self.table)
            .update(payload)
            .eq("id", template_id)
            .execute()
            .data,
        )
        return rows[0] if rows else None

    def exists(self, table: str, row_id: str) -> bool:
        rows = cast(
            Rows,
            self.db.table(table).select("id").eq("id", row_id).limit(1).execute().data,
        )
        return bool(rows)

    def get_category(self, category_id: str) -> dict[str, Any] | None:
        rows = cast(
            Rows,
            self.db.table("cashflow_categories")
            .select("*")
            .eq("id", category_id)
            .limit(1)
            .execute()
            .data,
        )
        return rows[0] if rows else None
