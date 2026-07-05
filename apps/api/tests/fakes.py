"""In-memory fake of the Supabase client for tests.

Mocks only at the database system boundary. Tests exercise the real FastAPI
router -> service -> repository stack through the public HTTP interface.
"""

import uuid
from typing import Any


class FakeResponse:
    def __init__(self, data: Any) -> None:
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
        # (column, operator, value) — operator is "eq" | "gte" | "lte" | "in".
        self.filters: list[tuple[str, str, Any]] = []
        self._orders: list[tuple[str, bool]] = []
        self._limit: int | None = None
        self._range: tuple[int, int] | None = None

    def select(self, _cols: str = "*") -> "FakeQuery":
        return self

    def eq(self, col: str, value: Any) -> "FakeQuery":
        self.filters.append((col, "eq", value))
        return self

    def neq(self, col: str, value: Any) -> "FakeQuery":
        self.filters.append((col, "neq", value))
        return self

    def gte(self, col: str, value: Any) -> "FakeQuery":
        self.filters.append((col, "gte", value))
        return self

    def lte(self, col: str, value: Any) -> "FakeQuery":
        self.filters.append((col, "lte", value))
        return self

    def in_(self, col: str, value: list[Any]) -> "FakeQuery":
        self.filters.append((col, "in", value))
        return self

    def order(self, col: str, desc: bool = False) -> "FakeQuery":
        self._orders.append((col, desc))
        return self

    def limit(self, n: int) -> "FakeQuery":
        self._limit = n
        return self

    def range(self, start: int, end: int) -> "FakeQuery":
        self._range = (start, end)
        return self

    @staticmethod
    def _cmp_ok(op: str, row_val: Any, value: Any) -> bool:
        if op == "eq":
            return row_val == value
        if op == "neq":
            return row_val != value
        if op == "in":
            return row_val in value
        if row_val is None:
            return False
        try:
            if op == "gte":
                return row_val >= value
            if op == "lte":
                return row_val <= value
        except TypeError:
            return False
        return False

    def _matches(self, row: dict[str, Any]) -> bool:
        return all(
            self._cmp_ok(op, row.get(col), value)
            for col, op, value in self.filters
        )

    def execute(self) -> FakeResponse:
        rows = self.client.tables.setdefault(self.table, [])
        if self.op == "select":
            result = [dict(r) for r in rows if self._matches(r)]
            # Apply each order clause in reverse so the first call dominates
            # (stable sort keeps prior relative order for equal keys).
            for col, desc in reversed(self._orders):
                result.sort(
                    key=lambda r: str(r.get(col) or ""),
                    reverse=desc,
                )
            if self._limit is not None:
                result = result[: self._limit]
            if self._range is not None:
                start, end = self._range
                result = result[start : end + 1]
            return FakeResponse(result)

        if self.op == "insert":
            if self.table in self.client.fail_insert_tables:
                raise RuntimeError(f"insert failed for {self.table}")
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


class FakeRpcQuery:
    def __init__(self, client: "FakeClient", fn: str, params: dict[str, Any]) -> None:
        self.client = client
        self.fn = fn
        self.params = params

    def execute(self) -> FakeResponse:
        self.client.rpc_calls.append((self.fn, dict(self.params)))
        if self.fn == "notification_unread_count":
            user_id = self.params["p_user_id"]
            count = sum(
                1
                for row in self.client.tables.setdefault("notifications", [])
                if row.get("user_id") == user_id and row.get("is_read") is False
            )
            return FakeResponse(count)
        raise AssertionError(f"unknown rpc {self.fn}")


class FakeClient:
    def __init__(self) -> None:
        self.tables: dict[str, list[dict[str, Any]]] = {}
        self.auth_users: dict[str, dict[str, Any]] = {}
        self.fail_insert_tables: set[str] = set()
        self.rpc_calls: list[tuple[str, dict[str, Any]]] = []
        self.auth = FakeAuth(self)

    def table(self, name: str) -> FakeTable:
        return FakeTable(self, name)

    def rpc(self, fn: str, params: dict[str, Any]) -> FakeRpcQuery:
        return FakeRpcQuery(self, fn, params)

    def seed(self, table: str, rows: list[dict[str, Any]]) -> None:
        self.tables.setdefault(table, []).extend(rows)