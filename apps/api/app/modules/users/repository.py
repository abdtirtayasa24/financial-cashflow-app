from typing import Any

from supabase import Client

from app.core.db import fetch_all, fetch_one, insert_one, update_one


class UserRepository:
    table = "user_profiles"

    def __init__(self, db: Client) -> None:
        self.db = db

    def list(self) -> list[dict[str, Any]]:
        return fetch_all(self.db, self.table, order="full_name")

    def get(self, user_id: str) -> dict[str, Any] | None:
        return fetch_one(self.db, self.table, user_id)

    def create_profile(self, payload: dict[str, Any]) -> dict[str, Any]:
        return insert_one(self.db, self.table, payload)

    def update_profile(
        self, user_id: str, payload: dict[str, Any]
    ) -> dict[str, Any] | None:
        return update_one(self.db, self.table, user_id, payload)

    def create_auth_user(self, email: str, password: str) -> str:
        """Create a Supabase Auth user and return its auth.users.id."""
        response = self.db.auth.admin.create_user(
            {"email": email, "password": password, "email_confirm": True}
        )
        return response.user.id