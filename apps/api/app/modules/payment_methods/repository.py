from typing import Any

from supabase import Client

from app.core.db import delete_one, fetch_all, fetch_one, insert_one, update_one


class PaymentMethodRepository:
    table = "payment_methods"

    def __init__(self, db: Client) -> None:
        self.db = db

    def list(self) -> list[dict[str, Any]]:
        return fetch_all(self.db, self.table, order="name")

    def get(self, method_id: str) -> dict[str, Any] | None:
        return fetch_one(self.db, self.table, method_id)

    def create(self, payload: dict[str, Any]) -> dict[str, Any]:
        return insert_one(self.db, self.table, payload)

    def update(self, method_id: str, payload: dict[str, Any]) -> dict[str, Any] | None:
        return update_one(self.db, self.table, method_id, payload)

    def delete(self, method_id: str) -> int:
        return delete_one(self.db, self.table, method_id)