from typing import Any, cast

from supabase import Client

from app.modules.transactions.repository import TransactionRepository

Rows = list[dict[str, Any]]


class TransactionImportRepository:
    def __init__(self, db: Client) -> None:
        self.db = db
        self.transactions = TransactionRepository(db)

    def department_by_code(self, code: str) -> dict[str, Any] | None:
        return self._one("departments", "code", code)

    def categories_by_name(self, name: str) -> Rows:
        return cast(
            Rows,
            self.db.table("cashflow_categories")
            .select("*")
            .eq("name", name)
            .execute()
            .data,
        )

    def cash_accounts_by_name(self, name: str) -> Rows:
        return cast(
            Rows,
            self.db.table("cash_accounts")
            .select("*")
            .eq("name", name)
            .execute()
            .data,
        )

    def payment_method_by_name(self, name: str) -> dict[str, Any] | None:
        return self._one("payment_methods", "name", name)

    def _one(self, table: str, col: str, value: str) -> dict[str, Any] | None:
        rows = cast(
            Rows,
            self.db.table(table).select("*").eq(col, value).limit(1).execute().data,
        )
        return rows[0] if rows else None
