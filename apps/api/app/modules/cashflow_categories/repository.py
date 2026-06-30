from typing import Any

from supabase import Client

from app.core.db import delete_one, fetch_all, fetch_one, insert_one, update_one


class CategoryRepository:
    table = "cashflow_categories"

    def __init__(self, db: Client) -> None:
        self.db = db

    def list(self) -> list[dict[str, Any]]:
        return fetch_all(self.db, self.table, order="name")

    def get(self, category_id: str) -> dict[str, Any] | None:
        return fetch_one(self.db, self.table, category_id)

    def create(self, payload: dict[str, Any]) -> dict[str, Any]:
        return insert_one(self.db, self.table, payload)

    def update(self, category_id: str, payload: dict[str, Any]) -> dict[str, Any] | None:
        return update_one(self.db, self.table, category_id, payload)

    def delete(self, category_id: str) -> int:
        return delete_one(self.db, self.table, category_id)