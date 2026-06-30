"""Thin data-access helpers over the Supabase query-builder client.

These are not an ORM. They wrap the supabase-py fluent builder to remove
duplication across repository modules while keeping direct, explicit queries.
"""

from collections.abc import Mapping
from typing import Any, cast

from supabase import Client


def _rows(resp: Any) -> list[dict[str, Any]]:
    return cast(list[dict[str, Any]], resp.data)


def fetch_one(db: Client, table: str, row_id: str) -> dict[str, Any] | None:
    resp = db.table(table).select("*").eq("id", row_id).limit(1).execute()
    rows = _rows(resp)
    return rows[0] if rows else None


def fetch_all(
    db: Client,
    table: str,
    *,
    eq: Mapping[str, Any] | None = None,
    order: str | None = None,
    desc: bool = False,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    query = db.table(table).select("*")
    if eq:
        for col, value in eq.items():
            query = query.eq(col, value)
    if order:
        query = query.order(order, desc=desc)
    if limit is not None:
        query = query.limit(limit)
    return _rows(query.execute())


def insert_one(db: Client, table: str, payload: dict[str, Any]) -> dict[str, Any]:
    return _rows(db.table(table).insert(payload).execute())[0]


def update_one(
    db: Client, table: str, row_id: str, payload: dict[str, Any]
) -> dict[str, Any] | None:
    rows = _rows(db.table(table).update(payload).eq("id", row_id).execute())
    return rows[0] if rows else None


def delete_one(db: Client, table: str, row_id: str) -> int:
    return len(_rows(db.table(table).delete().eq("id", row_id).execute()))