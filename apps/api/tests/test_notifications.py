"""Behavior tests for in-app notifications.

Exercises the real FastAPI router -> service -> repository path through HTTP,
mocked only at the Supabase client boundary (FakeClient).
"""

from __future__ import annotations

import uuid

from fastapi.testclient import TestClient

from tests.conftest import auth_header, make_token, seed_user
from tests.fakes import FakeClient

DEPT_OWN = "dept-own"
CASH_ACCOUNT = "ca-1"
CATEGORY = "cat-1"
PAYMENT_METHOD = "pm-1"


def seed_notification(
    db: FakeClient,
    *,
    user_id: str,
    notification_id: str | None = None,
    is_read: bool = False,
    related_transaction_id: str | None = None,
    created_at: str = "2026-07-01T00:00:00+00:00",
) -> str:
    notif_id = notification_id or str(uuid.uuid4())
    db.seed(
        "notifications",
        [
            {
                "id": notif_id,
                "user_id": user_id,
                "type": "PENDING_APPROVAL",
                "title": "Transaction pending approval",
                "message": "Transaction T-1 is awaiting finance review.",
                "related_transaction_id": related_transaction_id,
                "is_read": is_read,
                "created_at": created_at,
            }
        ],
    )
    return notif_id


def seed_transaction(
    db: FakeClient,
    *,
    created_by: str,
    status: str = "DRAFT",
    transaction_id: str | None = None,
) -> str:
    tx_id = transaction_id or str(uuid.uuid4())
    db.seed(
        "cashflow_transactions",
        [
            {
                "id": tx_id,
                "transaction_no": "INFLOW-202607-000001",
                "transaction_date": "2026-07-01",
                "direction": "INFLOW",
                "amount": 500_000,
                "currency": "IDR",
                "exchange_rate": 1.0,
                "base_amount": 500_000,
                "cash_account_id": CASH_ACCOUNT,
                "department_id": DEPT_OWN,
                "category_id": CATEGORY,
                "payment_method_id": PAYMENT_METHOD,
                "counterparty_name": "Acme",
                "reference_no": "REF-1",
                "description": "seeded",
                "status": status,
                "created_by": created_by,
                "submitted_at": None,
                "reviewed_by": None,
                "reviewed_at": None,
                "rejection_reason": None,
                "void_reason": None,
                "created_at": "2026-07-01T00:00:00+00:00",
                "updated_at": "2026-07-01T00:00:00+00:00",
            }
        ],
    )
    return tx_id


def test_user_lists_only_own_notifications_and_unread_count(
    client: TestClient, fake_db: FakeClient
) -> None:
    user_id = seed_user(fake_db, "EMPLOYEE", department_id=DEPT_OWN)
    other_id = seed_user(
        fake_db, "FINANCE_ADMIN", email="other@example.com", full_name="Other"
    )
    old_read = seed_notification(
        fake_db, user_id=user_id, is_read=True,
        created_at="2026-07-01T00:00:00+00:00",
    )
    newest_unread = seed_notification(
        fake_db, user_id=user_id, is_read=False,
        created_at="2026-07-02T00:00:00+00:00",
    )
    seed_notification(fake_db, user_id=other_id, is_read=False)

    token = auth_header(make_token(user_id))
    listing = client.get("/api/notifications", headers=token)
    assert listing.status_code == 200, listing.text
    ids = [row["id"] for row in listing.json()]
    assert ids == [newest_unread, old_read]

    count = client.get("/api/notifications/unread-count", headers=token)
    assert count.status_code == 200
    assert count.json() == {"count": 1}
    assert fake_db.rpc_calls[-1] == (
        "notification_unread_count",
        {"p_user_id": user_id},
    )


def test_user_marks_own_notification_as_read(
    client: TestClient, fake_db: FakeClient
) -> None:
    user_id = seed_user(fake_db, "EMPLOYEE", department_id=DEPT_OWN)
    notif_id = seed_notification(fake_db, user_id=user_id, is_read=False)
    token = auth_header(make_token(user_id))

    resp = client.post(f"/api/notifications/{notif_id}/read", headers=token)
    assert resp.status_code == 200, resp.text
    assert resp.json()["is_read"] is True
    count = client.get("/api/notifications/unread-count", headers=token)
    assert count.json() == {"count": 0}


def test_user_cannot_mark_another_users_notification_as_read(
    client: TestClient, fake_db: FakeClient
) -> None:
    user_id = seed_user(fake_db, "EMPLOYEE", department_id=DEPT_OWN)
    other_id = seed_user(
        fake_db, "FINANCE_ADMIN", email="other@example.com", full_name="Other"
    )
    notif_id = seed_notification(fake_db, user_id=other_id, is_read=False)

    resp = client.post(
        f"/api/notifications/{notif_id}/read",
        headers=auth_header(make_token(user_id)),
    )
    assert resp.status_code == 404


def test_user_marks_all_own_notifications_as_read(
    client: TestClient, fake_db: FakeClient
) -> None:
    user_id = seed_user(fake_db, "EMPLOYEE", department_id=DEPT_OWN)
    other_id = seed_user(
        fake_db, "FINANCE_ADMIN", email="other@example.com", full_name="Other"
    )
    seed_notification(fake_db, user_id=user_id, is_read=False)
    seed_notification(fake_db, user_id=user_id, is_read=False)
    seed_notification(fake_db, user_id=user_id, is_read=True)
    seed_notification(fake_db, user_id=other_id, is_read=False)

    token = auth_header(make_token(user_id))
    resp = client.post("/api/notifications/read-all", headers=token)
    assert resp.status_code == 200, resp.text
    assert resp.json() == {"updated": 2}
    assert client.get("/api/notifications/unread-count", headers=token).json() == {
        "count": 0
    }
    other_count = client.get(
        "/api/notifications/unread-count", headers=auth_header(make_token(other_id))
    )
    assert other_count.json() == {"count": 1}


def test_submitting_transaction_notifies_active_finance_admins(
    client: TestClient, fake_db: FakeClient
) -> None:
    employee_id = seed_user(fake_db, "EMPLOYEE", department_id=DEPT_OWN)
    active_finance = seed_user(
        fake_db, "FINANCE_ADMIN", email="finance@example.com", full_name="Finance"
    )
    inactive_finance = seed_user(
        fake_db, "FINANCE_ADMIN", status="INACTIVE",
        email="inactive@example.com", full_name="Inactive Finance",
    )
    manager_id = seed_user(
        fake_db, "DEPARTMENT_MANAGER", department_id=DEPT_OWN,
        email="manager@example.com", full_name="Manager",
    )
    tx_id = seed_transaction(fake_db, created_by=employee_id)

    resp = client.post(
        f"/api/transactions/{tx_id}/submit",
        headers=auth_header(make_token(employee_id)),
    )
    assert resp.status_code == 200, resp.text

    finance_notifications = client.get(
        "/api/notifications", headers=auth_header(make_token(active_finance))
    )
    assert finance_notifications.status_code == 200
    rows = finance_notifications.json()
    assert len(rows) == 1
    assert rows[0]["type"] == "PENDING_APPROVAL"
    assert rows[0]["related_transaction_id"] == tx_id
    assert "INFLOW-202607-000001" in rows[0]["message"]

    employee_notifications = client.get(
        "/api/notifications", headers=auth_header(make_token(employee_id))
    )
    manager_notifications = client.get(
        "/api/notifications", headers=auth_header(make_token(manager_id))
    )
    assert employee_notifications.json() == []
    assert manager_notifications.json() == []
    assert not any(
        row["user_id"] == inactive_finance
        for row in fake_db.tables.get("notifications", [])
    )


def test_notification_failure_does_not_block_submit_or_audit(
    client: TestClient, fake_db: FakeClient
) -> None:
    employee_id = seed_user(fake_db, "EMPLOYEE", department_id=DEPT_OWN)
    seed_user(
        fake_db, "FINANCE_ADMIN", email="finance@example.com", full_name="Finance"
    )
    tx_id = seed_transaction(fake_db, created_by=employee_id)
    fake_db.fail_insert_tables.add("notifications")

    resp = client.post(
        f"/api/transactions/{tx_id}/submit",
        headers=auth_header(make_token(employee_id)),
    )

    assert resp.status_code == 200, resp.text
    assert resp.json()["status"] == "SUBMITTED"
    logs = [lg for lg in fake_db.tables["transaction_audit_logs"]
            if lg["action"] == "SUBMIT"]
    assert len(logs) == 1


def test_resubmitting_rejected_transaction_does_not_duplicate_unread_notification(
    client: TestClient, fake_db: FakeClient
) -> None:
    employee_id = seed_user(fake_db, "EMPLOYEE", department_id=DEPT_OWN)
    finance_id = seed_user(
        fake_db, "FINANCE_ADMIN", email="finance@example.com", full_name="Finance"
    )
    tx_id = seed_transaction(fake_db, created_by=employee_id)
    emp_token = auth_header(make_token(employee_id))
    fin_token = auth_header(make_token(finance_id))

    first_submit = client.post(f"/api/transactions/{tx_id}/submit", headers=emp_token)
    assert first_submit.status_code == 200
    reject = client.post(
        f"/api/transactions/{tx_id}/reject",
        headers=fin_token,
        json={"reason": "Needs correction"},
    )
    assert reject.status_code == 200
    resubmit = client.post(f"/api/transactions/{tx_id}/submit", headers=emp_token)
    assert resubmit.status_code == 200

    notifications = client.get("/api/notifications", headers=fin_token).json()
    assert len(notifications) == 1
    assert notifications[0]["related_transaction_id"] == tx_id
    assert notifications[0]["is_read"] is False
