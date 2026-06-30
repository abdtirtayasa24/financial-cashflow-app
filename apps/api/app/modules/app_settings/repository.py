from typing import Any, cast

from supabase import Client

from app.core.db import insert_one, update_one


class AppSettingRepository:
    table = "app_settings"

    def __init__(self, db: Client) -> None:
        self.db = db

    def list(self) -> list[dict[str, Any]]:
        resp = self.db.table(self.table).select("*").order("key").execute()
        return cast(list[dict[str, Any]], resp.data)

    def get_by_key(self, key: str) -> dict[str, Any] | None:
        resp = (
            self.db.table(self.table)
            .select("*")
            .eq("key", key)
            .limit(1)
            .execute()
        )
        rows = cast(list[dict[str, Any]], resp.data)
        return rows[0] if rows else None

    def create(self, payload: dict[str, Any]) -> dict[str, Any]:
        return insert_one(self.db, self.table, payload)

    def update(self, setting_id: str, payload: dict[str, Any]) -> dict[str, Any] | None:
        return update_one(self.db, self.table, setting_id, payload)