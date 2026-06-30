"""In-memory fake of the Supabase client for tests.

Mocks only at the database system boundary. Tests exercise the real FastAPI
router -> service -> repository stack through the public HTTP interface.
"""

import uuid
from typing import Any


class FakeResponse:
    def __init__(self, data: list[dict[str, Any]]) -> None:
        self.data = data


class FakeAuthUser:
    def __init__(self, user_id: str) -> None:
        self.id = user_id


class FakeAuthUserResponse:
    def __init__(self, user_id: str) -> None:
        self.user = FakeAuthUser(user_id)


class FakeAuthAdmin:
    def __init__(self, client: "FakeClient") -> None:
        self.client = client

    def create_user(self, body: dict[str, Any]) -> FakeAuthUserResponse:
        user_id = str(uuid.uuid4())
        self.client.auth_users[user_id] = {"email": body["email"]}
        return FakeAuthUserResponse(user_id)


class FakeAuth:
    def __init__(self, client: "FakeClient") -> None:
        self.admin = FakeAuthAdmin(client)


class FakeQuery:
    def __init__(
        self,
        client: "FakeClient",
        table: str,
        op: str,
        payload: dict[str, Any] | list[dict[str, Any]] | None = None,
    ) -> None:
        self.client = client
        self.table = table
        self.op = op
        self.payload = payload
        self.filters: list[tuple[str, Any]] = []
        self._order: str | None = None
        self._desc = False
        self._limit: int | None = None

    def select(self, _cols: str = "*") -> "FakeQuery":
        return self

    def eq(self, col: str, value: Any) -> "FakeQuery":
        self.filters.append((col, value))
        return self

    def order(self, col: str, desc: bool = False) -> "FakeQuery":
        self._order = col
        self._desc = desc
        return self

    def limit(self, n: int) -> "FakeQuery":
        self._limit = n
        return self

    def _matches(self, row: dict[str, Any]) -> bool:
        return all(row.get(col) == value for col, value in self.filters)

    def execute(self) -> FakeResponse:
        rows = self.client.tables.setdefault(self.table, [])
        if self.op == "select":
            result = [dict(r) for r in rows if self._matches(r)]
            if self._order:
                result.sort(
                    key=lambda r: str(r.get(self._order) or ""),
                    reverse=self._desc,
                )
            if self._limit is not None:
                result = result[: self._limit]
            return FakeResponse(result)

        if self.op == "insert":
            items = self.payload if isinstance(self.payload, list) else [self.payload]
            out: list[dict[str, Any]] = []
            for item in items:
                row = dict(item)
                if not row.get("id"):
                    row["id"] = str(uuid.uuid4())
                row.setdefault("created_at", "2026-01-01T00:00:00+00:00")
                row.setdefault("updated_at", "2026-01-01T00:00:00+00:00")
                rows.append(row)
                out.append(dict(row))
            return FakeResponse(out)

        if self.op == "update":
            updated = []
            for row in rows:
                if self._matches(row):
                    row.update(self.payload)  # type: ignore[arg-type]
                    updated.append(dict(row))
            return FakeResponse(updated)

        if self.op == "delete":
            matched = [r for r in rows if self._matches(r)]
            self.client.tables[self.table] = [r for r in rows if not self._matches(r)]
            return FakeResponse([dict(r) for r in matched])

        raise AssertionError(f"unknown op {self.op}")


class FakeTable:
    def __init__(self, client: "FakeClient", table: str) -> None:
        self.client = client
        self.table = table

    def select(self, cols: str = "*") -> FakeQuery:
        _ = cols
        return FakeQuery(self.client, self.table, "select")

    def insert(self, payload: dict[str, Any] | list[dict[str, Any]]) -> FakeQuery:
        return FakeQuery(self.client, self.table, "insert", payload)

    def update(self, payload: dict[str, Any]) -> FakeQuery:
        return FakeQuery(self.client, self.table, "update", payload)

    def delete(self) -> FakeQuery:
        return FakeQuery(self.client, self.table, "delete")


class FakeClient:
    def __init__(self) -> None:
        self.tables: dict[str, list[dict[str, Any]]] = {}
        self.auth_users: dict[str, dict[str, Any]] = {}
        self.auth = FakeAuth(self)

    def table(self, name: str) -> FakeTable:
        return FakeTable(self, name)

    def seed(self, table: str, rows: list[dict[str, Any]]) -> None:
        self.tables.setdefault(table, []).extend(rows)