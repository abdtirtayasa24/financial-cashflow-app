"""Behavior tests for the cashflow transaction module.

Exercises the real router -> service -> repository stack through the public
HTTP interface, mocked only at the Supabase client boundary (FakeClient).
"""

from __future__ import annotations

import uuid

from fastapi.testclient import TestClient

from tests.conftest import auth_header, make_token, seed_user
from tests.fakes import FakeClient

DEPT_OWN = "dept-own"
DEPT_OTHER = "dept-other"
CASH_ACCOUNT = "ca-1"
CATEGORY = "cat-1"
PAYMENT_METHOD = "pm-1"


def _body(
    *,
    direction: str = "INFLOW",
    amount: float = 1_000_000,
    department_id: str = DEPT_OWN,
    payment_method_id: str = PAYMENT_METHOD,
    transaction_date: str = "2026-07-01",
) -> dict:
    return {
        "transaction_date": transaction_date,
        "direction": direction,
        "amount": amount,
        "cash_account_id": CASH_ACCOUNT,
        "department_id": department_id,
        "category_id": CATEGORY,
        "payment_method_id": payment_method_id,
        "counterparty_name": "Acme",
        "reference_no": "REF-1",
        "description": "test",
    }


def seed_transaction(
    db: FakeClient,
    *,
    created_by: str,
    status: str = "DRAFT",
    direction: str = "INFLOW",
    amount: float = 1_000_000,
    department_id: str = DEPT_OWN,
    transaction_no: str | None = None,
    transaction_id: str | None = None,
) -> str:
    tx_id = transaction_id or str(uuid.uuid4())
    db.seed(
        "cashflow_transactions",
        [
            {
                "id": tx_id,
                "transaction_no": transaction_no or "INFLOW-202607-000001",
                "transaction_date": "2026-07-01",
                "direction": direction,
                "amount": amount,
                "currency": "IDR",
                "exchange_rate": 1.0,
                "base_amount": amount,
                "cash_account_id": CASH_ACCOUNT,
                "department_id": department_id,
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


def _seed_threshold(db: FakeClient, enabled: bool, amount: str = "5000000") -> None:
    db.seed(
        "app_settings",
        [
            {"id": "s1", "key": "attachment_threshold_enabled",
             "value": "true" if enabled else "false", "updated_by": None,
             "updated_at": "2026-07-01T00:00:00+00:00",
             "created_at": "2026-07-01T00:00:00+00:00"},
            {"id": "s2", "key": "attachment_threshold_amount", "value": amount,
             "updated_by": None, "updated_at": "2026-07-01T00:00:00+00:00",
             "created_at": "2026-07-01T00:00:00+00:00"},
        ],
    )


# ── creation & transaction_no ──────────────────────────────────


def test_finance_admin_creates_for_any_department(
    client: TestClient, fake_db: FakeClient
) -> None:
    user_id = seed_user(fake_db, "FINANCE_ADMIN")
    resp = client.post(
        "/api/transactions", headers=auth_header(make_token(user_id)), json=_body()
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["status"] == "DRAFT"
    assert body["transaction_no"] == "INFLOW-202607-000001"
    assert body["base_amount"] == 1_000_000
    assert body["currency"] == "IDR"
    # CREATE audit log recorded.
    logs = fake_db.tables["transaction_audit_logs"]
    assert any(lg["action"] == "CREATE" for lg in logs)


def test_employee_creates_for_own_department(
    client: TestClient, fake_db: FakeClient
) -> None:
    user_id = seed_user(fake_db, "EMPLOYEE", department_id=DEPT_OWN)
    resp = client.post(
        "/api/transactions", headers=auth_header(make_token(user_id)), json=_body()
    )
    assert resp.status_code == 201
    assert resp.json()["created_by"] == user_id


def test_employee_cannot_create_for_other_department(
    client: TestClient, fake_db: FakeClient
) -> None:
    user_id = seed_user(fake_db, "EMPLOYEE", department_id=DEPT_OWN)
    resp = client.post(
        "/api/transactions",
        headers=auth_header(make_token(user_id)),
        json=_body(department_id=DEPT_OTHER),
    )
    assert resp.status_code == 403


def test_department_manager_cannot_create(
    client: TestClient, fake_db: FakeClient
) -> None:
    user_id = seed_user(fake_db, "DEPARTMENT_MANAGER", department_id=DEPT_OWN)
    resp = client.post(
        "/api/transactions", headers=auth_header(make_token(user_id)), json=_body()
    )
    assert resp.status_code == 403


def test_department_manager_cannot_edit_or_submit(
    client: TestClient, fake_db: FakeClient
) -> None:
    mgr_id = seed_user(fake_db, "DEPARTMENT_MANAGER", department_id=DEPT_OWN)
    tx_id = seed_transaction(fake_db, created_by=mgr_id, department_id=DEPT_OWN)
    token = auth_header(make_token(mgr_id))
    edit = client.patch(
        f"/api/transactions/{tx_id}", headers=token, json={"description": "x"}
    )
    assert edit.status_code == 403
    submit = client.post(f"/api/transactions/{tx_id}/submit", headers=token)
    assert submit.status_code == 403


def test_management_can_create_transaction_for_any_department(
    client: TestClient, fake_db: FakeClient
) -> None:
    user_id = seed_user(fake_db, "MANAGEMENT")
    resp = client.post(
        "/api/transactions", headers=auth_header(make_token(user_id)), json=_body()
    )
    assert resp.status_code == 201, resp.text
    assert resp.json()["created_by"] == user_id


def test_transaction_no_increments_per_direction_month(
    client: TestClient, fake_db: FakeClient
) -> None:
    user_id = seed_user(fake_db, "FINANCE_ADMIN")
    token = auth_header(make_token(user_id))
    first = client.post("/api/transactions", headers=token, json=_body()).json()
    second = client.post("/api/transactions", headers=token, json=_body()).json()
    third = client.post(
        "/api/transactions", headers=token, json=_body(direction="OUTFLOW")
    ).json()
    assert first["transaction_no"] == "INFLOW-202607-000001"
    assert second["transaction_no"] == "INFLOW-202607-000002"
    # Sequence is scoped per direction.
    assert third["transaction_no"] == "OUTFLOW-202607-000001"


def test_payment_method_required_on_create(
    client: TestClient, fake_db: FakeClient
) -> None:
    user_id = seed_user(fake_db, "FINANCE_ADMIN")
    body = _body()
    body["payment_method_id"] = ""
    resp = client.post(
        "/api/transactions", headers=auth_header(make_token(user_id)), json=body
    )
    # Pydantic rejects empty string for a required `str` field with 422.
    assert resp.status_code == 422


# ── viewing / scoping ──────────────────────────────────────────


def test_employee_views_only_own_transactions(
    client: TestClient, fake_db: FakeClient
) -> None:
    emp_id = seed_user(fake_db, "EMPLOYEE", department_id=DEPT_OWN)
    other_id = seed_user(
        fake_db, "EMPLOYEE", department_id=DEPT_OWN, email="o@x.com", full_name="Other"
    )
    own = seed_transaction(fake_db, created_by=emp_id, transaction_no="T-own")
    other = seed_transaction(fake_db, created_by=other_id, transaction_no="T-other")

    token = auth_header(make_token(emp_id))
    listing = client.get("/api/transactions", headers=token)
    assert listing.status_code == 200
    ids = [t["id"] for t in listing.json()]
    assert own in ids and other not in ids

    # Cannot fetch another user's transaction directly.
    resp = client.get(f"/api/transactions/{other}", headers=token)
    assert resp.status_code == 404


def test_department_manager_views_own_department_only(
    client: TestClient, fake_db: FakeClient
) -> None:
    mgr_id = seed_user(fake_db, "DEPARTMENT_MANAGER", department_id=DEPT_OWN)
    emp_other = seed_user(
        fake_db, "EMPLOYEE", department_id=DEPT_OTHER, email="o@x.com", full_name="O"
    )
    in_dept = seed_transaction(
        fake_db, created_by=emp_other, department_id=DEPT_OWN, transaction_no="T-in"
    )
    out_dept = seed_transaction(
        fake_db, created_by=emp_other, department_id=DEPT_OTHER, transaction_no="T-out"
    )
    token = auth_header(make_token(mgr_id))
    ids = [t["id"] for t in client.get("/api/transactions", headers=token).json()]
    assert in_dept in ids and out_dept not in ids


def test_finance_admin_views_all(client: TestClient, fake_db: FakeClient) -> None:
    fin_id = seed_user(fake_db, "FINANCE_ADMIN")
    emp_id = seed_user(fake_db, "EMPLOYEE", department_id=DEPT_OWN, email="e@x.com")
    seed_transaction(fake_db, created_by=emp_id, department_id=DEPT_OTHER,
                     transaction_no="T-1")
    token = auth_header(make_token(fin_id))
    assert len(client.get("/api/transactions", headers=token).json()) == 1


def test_management_views_all_transactions(
    client: TestClient, fake_db: FakeClient
) -> None:
    mgmt_id = seed_user(fake_db, "MANAGEMENT")
    emp_id = seed_user(fake_db, "EMPLOYEE", department_id=DEPT_OWN, email="e@x.com")
    seed_transaction(fake_db, created_by=emp_id, transaction_no="T-1")
    token = auth_header(make_token(mgmt_id))
    assert len(client.get("/api/transactions", headers=token).json()) == 1


def test_list_filters_by_status_and_direction(
    client: TestClient, fake_db: FakeClient
) -> None:
    fin_id = seed_user(fake_db, "FINANCE_ADMIN")
    seed_transaction(fake_db, created_by=fin_id, status="DRAFT", direction="INFLOW",
                     transaction_no="I-1")
    seed_transaction(fake_db, created_by=fin_id, status="SUBMITTED", direction="OUTFLOW",
                     transaction_no="O-1")
    token = auth_header(make_token(fin_id))
    inflow = client.get("/api/transactions?direction=INFLOW", headers=token).json()
    assert len(inflow) == 1 and inflow[0]["direction"] == "INFLOW"
    drafts = client.get("/api/transactions?status=DRAFT", headers=token).json()
    assert len(drafts) == 1 and drafts[0]["status"] == "DRAFT"


# ── editing ────────────────────────────────────────────────────


def test_owner_can_edit_draft_and_audit_logged(
    client: TestClient, fake_db: FakeClient
) -> None:
    emp_id = seed_user(fake_db, "EMPLOYEE", department_id=DEPT_OWN)
    tx_id = seed_transaction(fake_db, created_by=emp_id)
    resp = client.patch(
        f"/api/transactions/{tx_id}",
        headers=auth_header(make_token(emp_id)),
        json={"amount": 2_000_000, "description": "updated"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["amount"] == 2_000_000
    assert body["base_amount"] == 2_000_000
    logs = [lg for lg in fake_db.tables["transaction_audit_logs"]
            if lg["action"] == "UPDATE"]
    assert logs and logs[-1]["old_value"]["amount"] == 1_000_000
    assert logs[-1]["new_value"]["amount"] == 2_000_000


def test_rejected_transaction_can_be_ed(
    client: TestClient, fake_db: FakeClient
) -> None:
    emp_id = seed_user(fake_db, "EMPLOYEE", department_id=DEPT_OWN)
    tx_id = seed_transaction(fake_db, created_by=emp_id, status="REJECTED")
    resp = client.patch(
        f"/api/transactions/{tx_id}",
        headers=auth_header(make_token(emp_id)),
        json={"description": "fixed"},
    )
    assert resp.status_code == 200


def test_approved_cannot_be_edited(
    client: TestClient, fake_db: FakeClient
) -> None:
    fin_id = seed_user(fake_db, "FINANCE_ADMIN")
    tx_id = seed_transaction(fake_db, created_by=fin_id, status="APPROVED")
    resp = client.patch(
        f"/api/transactions/{tx_id}",
        headers=auth_header(make_token(fin_id)),
        json={"description": "x"},
    )
    assert resp.status_code == 409


def test_submitted_cannot_be_edited(
    client: TestClient, fake_db: FakeClient
) -> None:
    fin_id = seed_user(fake_db, "FINANCE_ADMIN")
    tx_id = seed_transaction(fake_db, created_by=fin_id, status="SUBMITTED")
    resp = client.patch(
        f"/api/transactions/{tx_id}",
        headers=auth_header(make_token(fin_id)),
        json={"description": "x"},
    )
    assert resp.status_code == 409


def test_employee_cannot_edit_others_transaction(
    client: TestClient, fake_db: FakeClient
) -> None:
    emp_id = seed_user(fake_db, "EMPLOYEE", department_id=DEPT_OWN)
    other_id = seed_user(
        fake_db, "EMPLOYEE", department_id=DEPT_OWN, email="o@x.com", full_name="O"
    )
    tx_id = seed_transaction(fake_db, created_by=other_id)
    resp = client.patch(
        f"/api/transactions/{tx_id}",
        headers=auth_header(make_token(emp_id)),
        json={"description": "x"},
    )
    assert resp.status_code == 403


# ── submission & attachment threshold ──────────────────────────


def test_submit_draft_succeeds(client: TestClient, fake_db: FakeClient) -> None:
    emp_id = seed_user(fake_db, "EMPLOYEE", department_id=DEPT_OWN)
    tx_id = seed_transaction(fake_db, created_by=emp_id, amount=500_000)
    resp = client.post(
        f"/api/transactions/{tx_id}/submit", headers=auth_header(make_token(emp_id))
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "SUBMITTED"
    assert body["submitted_at"] is not None
    logs = [lg for lg in fake_db.tables["transaction_audit_logs"]
            if lg["action"] == "SUBMIT"]
    assert logs


def test_rejected_resubmits_directly_to_submitted(
    client: TestClient, fake_db: FakeClient
) -> None:
    emp_id = seed_user(fake_db, "EMPLOYEE", department_id=DEPT_OWN)
    tx_id = seed_transaction(fake_db, created_by=emp_id, status="REJECTED",
                             amount=500_000)
    resp = client.post(
        f"/api/transactions/{tx_id}/submit", headers=auth_header(make_token(emp_id))
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "SUBMITTED"


def test_threshold_blocks_submission_without_attachment(
    client: TestClient, fake_db: FakeClient
) -> None:
    _seed_threshold(fake_db, enabled=True, amount="5000000")
    fin_id = seed_user(fake_db, "FINANCE_ADMIN")
    tx_id = seed_transaction(fake_db, created_by=fin_id, amount=5_000_000)
    resp = client.post(
        f"/api/transactions/{tx_id}/submit", headers=auth_header(make_token(fin_id))
    )
    assert resp.status_code == 422
    assert "Attachments are required" in resp.json()["detail"]


def test_threshold_disabled_does_not_block(
    client: TestClient, fake_db: FakeClient
) -> None:
    _seed_threshold(fake_db, enabled=False)
    fin_id = seed_user(fake_db, "FINANCE_ADMIN")
    tx_id = seed_transaction(fake_db, created_by=fin_id, amount=5_000_000)
    resp = client.post(
        f"/api/transactions/{tx_id}/submit", headers=auth_header(make_token(fin_id))
    )
    assert resp.status_code == 200


def test_threshold_below_amount_does_not_block(
    client: TestClient, fake_db: FakeClient
) -> None:
    _seed_threshold(fake_db, enabled=True, amount="5000000")
    fin_id = seed_user(fake_db, "FINANCE_ADMIN")
    tx_id = seed_transaction(fake_db, created_by=fin_id, amount=4_999_999)
    resp = client.post(
        f"/api/transactions/{tx_id}/submit", headers=auth_header(make_token(fin_id))
    )
    assert resp.status_code == 200


# ── finance approval workflow ──────────────────────────────────


def test_finance_admin_approves_submitted_transaction(
    client: TestClient, fake_db: FakeClient
) -> None:
    fin_id = seed_user(fake_db, "FINANCE_ADMIN")
    tx_id = seed_transaction(fake_db, created_by=fin_id, status="SUBMITTED")
    resp = client.post(
        f"/api/transactions/{tx_id}/approve", headers=auth_header(make_token(fin_id))
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["status"] == "APPROVED"
    assert body["reviewed_by"] == fin_id
    assert body["reviewed_at"] is not None
    logs = [lg for lg in fake_db.tables["transaction_audit_logs"]
            if lg["action"] == "APPROVE"]
    assert logs
    assert logs[-1]["actor_user_id"] == fin_id
    assert logs[-1]["old_value"] == {"status": "SUBMITTED"}
    assert logs[-1]["new_value"]["status"] == "APPROVED"
    assert logs[-1]["new_value"]["reviewed_by"] == fin_id


def test_approve_requires_submitted_status(
    client: TestClient, fake_db: FakeClient
) -> None:
    fin_id = seed_user(fake_db, "FINANCE_ADMIN")
    tx_id = seed_transaction(fake_db, created_by=fin_id, status="DRAFT")
    resp = client.post(
        f"/api/transactions/{tx_id}/approve", headers=auth_header(make_token(fin_id))
    )
    assert resp.status_code == 409


def test_approve_second_call_conflicts_without_duplicate_audit(
    client: TestClient, fake_db: FakeClient
) -> None:
    fin_id = seed_user(fake_db, "FINANCE_ADMIN")
    token = auth_header(make_token(fin_id))
    tx_id = seed_transaction(fake_db, created_by=fin_id, status="SUBMITTED")
    first = client.post(f"/api/transactions/{tx_id}/approve", headers=token)
    assert first.status_code == 200
    resp = client.post(f"/api/transactions/{tx_id}/approve", headers=token)
    assert resp.status_code == 409
    logs = [lg for lg in fake_db.tables["transaction_audit_logs"]
            if lg["action"] == "APPROVE"]
    assert len(logs) == 1


def test_non_finance_users_cannot_approve(
    client: TestClient, fake_db: FakeClient
) -> None:
    creator_id = seed_user(fake_db, "FINANCE_ADMIN", email="creator@x.com")
    tx_id = seed_transaction(fake_db, created_by=creator_id, status="SUBMITTED")
    roles = [
        ("EMPLOYEE", DEPT_OWN),
        ("DEPARTMENT_MANAGER", DEPT_OWN),
        ("SYSTEM_ADMIN", None),
    ]
    for i, (role, department_id) in enumerate(roles):
        user_id = seed_user(
            fake_db, role, department_id=department_id,
            email=f"role-{i}@x.com", full_name=f"Role {i}",
        )
        resp = client.post(
            f"/api/transactions/{tx_id}/approve",
            headers=auth_header(make_token(user_id)),
        )
        assert resp.status_code == 403


def test_finance_admin_rejects_submitted_transaction_with_reason(
    client: TestClient, fake_db: FakeClient
) -> None:
    fin_id = seed_user(fake_db, "FINANCE_ADMIN")
    tx_id = seed_transaction(fake_db, created_by=fin_id, status="SUBMITTED")
    resp = client.post(
        f"/api/transactions/{tx_id}/reject",
        headers=auth_header(make_token(fin_id)),
        json={"reason": "Missing receipt"},
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["status"] == "REJECTED"
    assert body["reviewed_by"] == fin_id
    assert body["reviewed_at"] is not None
    assert body["rejection_reason"] == "Missing receipt"
    logs = [lg for lg in fake_db.tables["transaction_audit_logs"]
            if lg["action"] == "REJECT"]
    assert logs
    assert logs[-1]["reason"] == "Missing receipt"
    assert logs[-1]["old_value"] == {"status": "SUBMITTED"}
    assert logs[-1]["new_value"]["status"] == "REJECTED"
    assert logs[-1]["new_value"]["rejection_reason"] == "Missing receipt"


def test_reject_requires_reason(client: TestClient, fake_db: FakeClient) -> None:
    fin_id = seed_user(fake_db, "FINANCE_ADMIN")
    tx_id = seed_transaction(fake_db, created_by=fin_id, status="SUBMITTED")
    missing = client.post(
        f"/api/transactions/{tx_id}/reject", headers=auth_header(make_token(fin_id)),
        json={},
    )
    empty = client.post(
        f"/api/transactions/{tx_id}/reject", headers=auth_header(make_token(fin_id)),
        json={"reason": ""},
    )
    blank = client.post(
        f"/api/transactions/{tx_id}/reject", headers=auth_header(make_token(fin_id)),
        json={"reason": "   "},
    )
    assert missing.status_code == 422
    assert empty.status_code == 422
    assert blank.status_code == 422


def test_reject_requires_submitted_status(
    client: TestClient, fake_db: FakeClient
) -> None:
    fin_id = seed_user(fake_db, "FINANCE_ADMIN")
    tx_id = seed_transaction(fake_db, created_by=fin_id, status="APPROVED")
    resp = client.post(
        f"/api/transactions/{tx_id}/reject",
        headers=auth_header(make_token(fin_id)),
        json={"reason": "Wrong state"},
    )
    assert resp.status_code == 409


def test_reject_second_call_conflicts_without_duplicate_audit(
    client: TestClient, fake_db: FakeClient
) -> None:
    fin_id = seed_user(fake_db, "FINANCE_ADMIN")
    token = auth_header(make_token(fin_id))
    tx_id = seed_transaction(fake_db, created_by=fin_id, status="SUBMITTED")
    first = client.post(
        f"/api/transactions/{tx_id}/reject",
        headers=token,
        json={"reason": "Missing receipt"},
    )
    assert first.status_code == 200
    second = client.post(
        f"/api/transactions/{tx_id}/reject",
        headers=token,
        json={"reason": "Second reason"},
    )
    assert second.status_code == 409
    logs = [lg for lg in fake_db.tables["transaction_audit_logs"]
            if lg["action"] == "REJECT"]
    assert len(logs) == 1
    assert logs[0]["reason"] == "Missing receipt"


def test_management_can_submit_transaction(
    client: TestClient, fake_db: FakeClient
) -> None:
    emp_id = seed_user(fake_db, "EMPLOYEE", department_id=DEPT_OWN)
    mgmt_id = seed_user(fake_db, "MANAGEMENT")
    tx_id = seed_transaction(fake_db, created_by=emp_id)

    resp = client.post(
        f"/api/transactions/{tx_id}/submit",
        headers=auth_header(make_token(mgmt_id)),
    )

    assert resp.status_code == 200, resp.text
    assert resp.json()["status"] == "SUBMITTED"


def test_management_can_approve_submitted_transaction(
    client: TestClient, fake_db: FakeClient
) -> None:
    creator_id = seed_user(fake_db, "FINANCE_ADMIN", email="creator@x.com")
    mgmt_id = seed_user(fake_db, "MANAGEMENT")
    tx_id = seed_transaction(
        fake_db, created_by=creator_id, status="SUBMITTED", transaction_no="T-S"
    )

    resp = client.post(
        f"/api/transactions/{tx_id}/approve",
        headers=auth_header(make_token(mgmt_id)),
    )

    assert resp.status_code == 200, resp.text
    assert resp.json()["status"] == "APPROVED"
    assert resp.json()["reviewed_by"] == mgmt_id


def test_management_can_reject_and_void_transactions(
    client: TestClient, fake_db: FakeClient
) -> None:
    creator_id = seed_user(fake_db, "FINANCE_ADMIN", email="creator@x.com")
    mgmt_id = seed_user(fake_db, "MANAGEMENT")
    submitted = seed_transaction(
        fake_db, created_by=creator_id, status="SUBMITTED", transaction_no="T-S"
    )
    approved = seed_transaction(
        fake_db, created_by=creator_id, status="APPROVED", transaction_no="T-A"
    )
    token = auth_header(make_token(mgmt_id))

    reject = client.post(
        f"/api/transactions/{submitted}/reject",
        headers=token,
        json={"reason": "No"},
    )
    void = client.post(
        f"/api/transactions/{approved}/void",
        headers=token,
        json={"reason": "Duplicate"},
    )

    assert reject.status_code == 200, reject.text
    assert reject.json()["status"] == "REJECTED"
    assert void.status_code == 200, void.text
    assert void.json()["status"] == "VOIDED"


def test_non_finance_users_cannot_reject_or_void(
    client: TestClient, fake_db: FakeClient
) -> None:
    creator_id = seed_user(fake_db, "FINANCE_ADMIN", email="creator@x.com")
    submitted = seed_transaction(
        fake_db, created_by=creator_id, status="SUBMITTED", transaction_no="T-S"
    )
    approved = seed_transaction(
        fake_db, created_by=creator_id, status="APPROVED", transaction_no="T-A"
    )
    roles = [
        ("EMPLOYEE", DEPT_OWN),
        ("DEPARTMENT_MANAGER", DEPT_OWN),
        ("SYSTEM_ADMIN", None),
    ]
    for i, (role, department_id) in enumerate(roles):
        user_id = seed_user(
            fake_db, role, department_id=department_id,
            email=f"reject-void-{i}@x.com", full_name=f"Role {i}",
        )
        token = auth_header(make_token(user_id))
        reject = client.post(
            f"/api/transactions/{submitted}/reject",
            headers=token,
            json={"reason": "No"},
        )
        void = client.post(
            f"/api/transactions/{approved}/void",
            headers=token,
            json={"reason": "No"},
        )
        assert reject.status_code == 403
        assert void.status_code == 403


def test_finance_admin_voids_approved_transaction_with_reason(
    client: TestClient, fake_db: FakeClient
) -> None:
    fin_id = seed_user(fake_db, "FINANCE_ADMIN")
    tx_id = seed_transaction(fake_db, created_by=fin_id, status="APPROVED")
    resp = client.post(
        f"/api/transactions/{tx_id}/void",
        headers=auth_header(make_token(fin_id)),
        json={"reason": "Duplicate transaction"},
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["status"] == "VOIDED"
    assert body["void_reason"] == "Duplicate transaction"
    assert body["status"] != "APPROVED"
    logs = [lg for lg in fake_db.tables["transaction_audit_logs"]
            if lg["action"] == "VOID"]
    assert logs
    assert logs[-1]["reason"] == "Duplicate transaction"
    assert logs[-1]["old_value"] == {"status": "APPROVED"}
    assert logs[-1]["new_value"] == {
        "status": "VOIDED",
        "void_reason": "Duplicate transaction",
    }


def test_void_requires_reason(client: TestClient, fake_db: FakeClient) -> None:
    fin_id = seed_user(fake_db, "FINANCE_ADMIN")
    tx_id = seed_transaction(fake_db, created_by=fin_id, status="APPROVED")
    missing = client.post(
        f"/api/transactions/{tx_id}/void", headers=auth_header(make_token(fin_id)),
        json={},
    )
    empty = client.post(
        f"/api/transactions/{tx_id}/void", headers=auth_header(make_token(fin_id)),
        json={"reason": ""},
    )
    blank = client.post(
        f"/api/transactions/{tx_id}/void", headers=auth_header(make_token(fin_id)),
        json={"reason": "   "},
    )
    assert missing.status_code == 422
    assert empty.status_code == 422
    assert blank.status_code == 422


def test_void_requires_approved_status(
    client: TestClient, fake_db: FakeClient
) -> None:
    fin_id = seed_user(fake_db, "FINANCE_ADMIN")
    tx_id = seed_transaction(fake_db, created_by=fin_id, status="SUBMITTED")
    resp = client.post(
        f"/api/transactions/{tx_id}/void",
        headers=auth_header(make_token(fin_id)),
        json={"reason": "Wrong state"},
    )
    assert resp.status_code == 409


def test_void_second_call_conflicts_without_duplicate_audit(
    client: TestClient, fake_db: FakeClient
) -> None:
    fin_id = seed_user(fake_db, "FINANCE_ADMIN")
    token = auth_header(make_token(fin_id))
    tx_id = seed_transaction(fake_db, created_by=fin_id, status="APPROVED")
    first = client.post(
        f"/api/transactions/{tx_id}/void",
        headers=token,
        json={"reason": "Duplicate"},
    )
    assert first.status_code == 200
    second = client.post(
        f"/api/transactions/{tx_id}/void",
        headers=token,
        json={"reason": "Second reason"},
    )
    assert second.status_code == 409
    logs = [lg for lg in fake_db.tables["transaction_audit_logs"]
            if lg["action"] == "VOID"]
    assert len(logs) == 1
    assert logs[0]["reason"] == "Duplicate"


# ── deletion ───────────────────────────────────────────────────


def test_management_can_delete_draft(
    client: TestClient, fake_db: FakeClient
) -> None:
    creator_id = seed_user(fake_db, "FINANCE_ADMIN", email="creator@x.com")
    mgmt_id = seed_user(fake_db, "MANAGEMENT")
    tx_id = seed_transaction(fake_db, created_by=creator_id)

    resp = client.delete(
        f"/api/transactions/{tx_id}", headers=auth_header(make_token(mgmt_id))
    )

    assert resp.status_code == 204
    assert not any(t["id"] == tx_id for t in fake_db.tables["cashflow_transactions"])


def test_owner_can_delete_draft(
    client: TestClient, fake_db: FakeClient
) -> None:
    emp_id = seed_user(fake_db, "EMPLOYEE", department_id=DEPT_OWN)
    tx_id = seed_transaction(fake_db, created_by=emp_id)
    resp = client.delete(
        f"/api/transactions/{tx_id}", headers=auth_header(make_token(emp_id))
    )
    assert resp.status_code == 204
    assert not any(t["id"] == tx_id for t in fake_db.tables["cashflow_transactions"])


def test_delete_cascades_to_attachments_and_audit(
    client: TestClient, fake_db: FakeClient
) -> None:
    fin_id = seed_user(fake_db, "FINANCE_ADMIN")
    tx_id = seed_transaction(fake_db, created_by=fin_id, status="REJECTED")
    fake_db.seed(
        "transaction_attachments",
        [
            {"id": "a1", "transaction_id": tx_id, "original_file_name": "r.pdf",
             "stored_file_name": "x.pdf", "relative_path": "transactions/2026/07/t/x.pdf",
             "mime_type": "application/pdf", "file_size_bytes": 10,
             "checksum_sha256": "h", "uploaded_by": fin_id,
             "uploaded_at": "2026-07-01T00:00:00+00:00"}
        ],
    )
    resp = client.delete(
        f"/api/transactions/{tx_id}", headers=auth_header(make_token(fin_id))
    )
    assert resp.status_code == 204
    assert not any(a["transaction_id"] == tx_id
                   for a in fake_db.tables.get("transaction_attachments", []))
    assert not any(log["transaction_id"] == tx_id
                   for log in fake_db.tables.get("transaction_audit_logs", []))


def test_submitted_cannot_be_deleted(
    client: TestClient, fake_db: FakeClient
) -> None:
    fin_id = seed_user(fake_db, "FINANCE_ADMIN")
    tx_id = seed_transaction(fake_db, created_by=fin_id, status="SUBMITTED")
    resp = client.delete(
        f"/api/transactions/{tx_id}", headers=auth_header(make_token(fin_id))
    )
    assert resp.status_code == 409


def test_approved_cannot_be_deleted(
    client: TestClient, fake_db: FakeClient
) -> None:
    fin_id = seed_user(fake_db, "FINANCE_ADMIN")
    tx_id = seed_transaction(fake_db, created_by=fin_id, status="APPROVED")
    resp = client.delete(
        f"/api/transactions/{tx_id}", headers=auth_header(make_token(fin_id))
    )
    assert resp.status_code == 409


def test_employee_cannot_delete_others_draft(
    client: TestClient, fake_db: FakeClient
) -> None:
    emp_id = seed_user(fake_db, "EMPLOYEE", department_id=DEPT_OWN)
    other_id = seed_user(
        fake_db, "EMPLOYEE", department_id=DEPT_OWN, email="o@x.com", full_name="O"
    )
    tx_id = seed_transaction(fake_db, created_by=other_id)
    resp = client.delete(
        f"/api/transactions/{tx_id}", headers=auth_header(make_token(emp_id))
    )
    assert resp.status_code == 403


# ── audit trail ────────────────────────────────────────────────


def test_audit_logs_include_actor_name(
    client: TestClient, fake_db: FakeClient
) -> None:
    fin_id = seed_user(fake_db, "FINANCE_ADMIN", full_name="Fin Admin")
    token = auth_header(make_token(fin_id))
    tx_id = client.post("/api/transactions", headers=token, json=_body()).json()["id"]
    client.post(f"/api/transactions/{tx_id}/submit", headers=token)
    logs = client.get(
        f"/api/transactions/{tx_id}/audit-logs", headers=token
    ).json()
    actions = [lg["action"] for lg in logs]
    assert "CREATE" in actions and "SUBMIT" in actions
    assert all(lg["actor_name"] == "Fin Admin" for lg in logs)


# ── review-fix regressions ─────────────────────────────────────


def test_department_manager_without_department_cannot_list(
    client: TestClient, fake_db: FakeClient
) -> None:
    # A manager with no department must not get an unscoped (all-rows) list.
    mgr_id = seed_user(fake_db, "DEPARTMENT_MANAGER", department_id=None)
    resp = client.get("/api/transactions", headers=auth_header(make_token(mgr_id)))
    assert resp.status_code == 403


def test_system_admin_can_view_but_not_mutate(
    client: TestClient, fake_db: FakeClient
) -> None:
    admin_id = seed_user(fake_db, "SYSTEM_ADMIN")
    fin_id = seed_user(fake_db, "FINANCE_ADMIN", email="f@x.com", full_name="Fin")
    tx_id = seed_transaction(fake_db, created_by=fin_id, transaction_no="T-1")
    token = auth_header(make_token(admin_id))

    assert client.get("/api/transactions", headers=token).status_code == 200
    assert client.get(f"/api/transactions/{tx_id}", headers=token).status_code == 200
    # System Admin cannot create / edit / submit / delete transactions.
    assert client.post(
        "/api/transactions", headers=token, json=_body()
    ).status_code == 403
    assert client.patch(
        f"/api/transactions/{tx_id}", headers=token, json={"description": "x"}
    ).status_code == 403
    assert client.post(
        f"/api/transactions/{tx_id}/submit", headers=token
    ).status_code == 403
    assert client.delete(
        f"/api/transactions/{tx_id}", headers=token
    ).status_code == 403


def test_edit_direction_regenerates_transaction_no(
    client: TestClient, fake_db: FakeClient
) -> None:
    fin_id = seed_user(fake_db, "FINANCE_ADMIN")
    tx_id = seed_transaction(
        fake_db, created_by=fin_id, direction="INFLOW",
        transaction_no="INFLOW-202607-000001",
    )
    resp = client.patch(
        f"/api/transactions/{tx_id}",
        headers=auth_header(make_token(fin_id)),
        json={"direction": "OUTFLOW"},
    )
    assert resp.status_code == 200
    assert resp.json()["transaction_no"] == "OUTFLOW-202607-000001"
    assert resp.json()["direction"] == "OUTFLOW"


def test_edit_date_regenerates_transaction_no(
    client: TestClient, fake_db: FakeClient
) -> None:
    fin_id = seed_user(fake_db, "FINANCE_ADMIN")
    tx_id = seed_transaction(
        fake_db, created_by=fin_id,
        transaction_no="INFLOW-202607-000001",
    )
    resp = client.patch(
        f"/api/transactions/{tx_id}",
        headers=auth_header(make_token(fin_id)),
        json={"transaction_date": "2026-08-15"},
    )
    assert resp.status_code == 200
    assert resp.json()["transaction_no"] == "INFLOW-202608-000001"


def test_resubmit_clears_rejection_fields(
    client: TestClient, fake_db: FakeClient
) -> None:
    emp_id = seed_user(fake_db, "EMPLOYEE", department_id=DEPT_OWN)
    tx_id = seed_transaction(
        fake_db, created_by=emp_id, status="REJECTED", amount=500_000,
    )
    # Simulate prior review metadata from a rejection.
    fake_db.tables["cashflow_transactions"][-1].update(
        {
            "rejection_reason": "Missing receipt",
            "reviewed_by": emp_id,
            "reviewed_at": "2026-07-01T00:00:00+00:00",
        }
    )
    resp = client.post(
        f"/api/transactions/{tx_id}/submit", headers=auth_header(make_token(emp_id))
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "SUBMITTED"
    assert body["rejection_reason"] is None
    assert body["reviewed_by"] is None
    assert body["reviewed_at"] is None


def test_list_pagination(
    client: TestClient, fake_db: FakeClient
) -> None:
    fin_id = seed_user(fake_db, "FINANCE_ADMIN")
    for i in range(3):
        seed_transaction(
            fake_db, created_by=fin_id, transaction_no=f"INFLOW-202607-{i:06d}",
            transaction_id=f"tx-{i}",
        )
    token = auth_header(make_token(fin_id))
    page1 = client.get("/api/transactions?limit=2&offset=0", headers=token).json()
    page2 = client.get("/api/transactions?limit=2&offset=2", headers=token).json()
    assert len(page1) == 2
    assert len(page2) == 1