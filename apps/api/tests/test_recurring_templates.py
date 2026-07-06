"""Behavior tests for recurring transaction template APIs."""

from __future__ import annotations

from fastapi.testclient import TestClient

from tests.conftest import auth_header, make_token, seed_user
from tests.fakes import FakeClient

DEPT_OWN = "dept-own"
DEPT_OTHER = "dept-other"
CAT_ID = "cat-1"
CASH_ID = "cash-1"
PAYMENT_METHOD_ID = "pm-1"


def _body(
    *,
    department_id: str = DEPT_OWN,
    submission_mode: str = "DRAFT",
    next_run_date: str = "2026-08-01",
) -> dict[str, object]:
    return {
        "department_id": department_id,
        "category_id": CAT_ID,
        "cash_account_id": CASH_ID,
        "payment_method_id": PAYMENT_METHOD_ID,
        "direction": "OUTFLOW",
        "amount": 1_000_000,
        "counterparty_name": "ACME Corp",
        "reference_no": "REC-1",
        "description": "Monthly recurring expense",
        "submission_mode": submission_mode,
        "frequency": "MONTHLY",
        "interval": 1,
        "next_run_date": next_run_date,
        "end_date": None,
    }


def _seed_refs(db: FakeClient) -> None:
    db.seed(
        "departments",
        [
            {"id": DEPT_OWN, "name": "Own", "code": "OWN", "is_active": True},
            {"id": DEPT_OTHER, "name": "Other", "code": "OTH", "is_active": True},
        ],
    )
    db.seed(
        "cashflow_categories",
        [
            {"id": CAT_ID, "name": "Rent", "direction": "OUTFLOW", "is_active": True},
        ],
    )
    db.seed(
        "cash_accounts",
        [
            {"id": CASH_ID, "name": "Main", "is_active": True},
        ],
    )
    db.seed(
        "payment_methods",
        [
            {"id": PAYMENT_METHOD_ID, "name": "Transfer", "is_active": True},
        ],
    )


def test_finance_admin_can_create_auto_submit_template(
    client: TestClient, fake_db: FakeClient
) -> None:
    _seed_refs(fake_db)
    user_id = seed_user(fake_db, "FINANCE_ADMIN")

    resp = client.post(
        "/api/recurring-templates",
        headers=auth_header(make_token(user_id)),
        json=_body(submission_mode="AUTO_SUBMIT", department_id=DEPT_OTHER),
    )

    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["submission_mode"] == "AUTO_SUBMIT"
    assert body["department_id"] == DEPT_OTHER
    assert body["created_by"] == user_id
    assert body["is_active"] is True


def test_employee_cannot_create_auto_submit_template(
    client: TestClient, fake_db: FakeClient
) -> None:
    _seed_refs(fake_db)
    user_id = seed_user(fake_db, "EMPLOYEE", department_id=DEPT_OWN)

    resp = client.post(
        "/api/recurring-templates",
        headers=auth_header(make_token(user_id)),
        json=_body(submission_mode="AUTO_SUBMIT", department_id=DEPT_OWN),
    )

    assert resp.status_code == 403


def test_employee_cannot_create_template_for_other_department(
    client: TestClient, fake_db: FakeClient
) -> None:
    _seed_refs(fake_db)
    user_id = seed_user(fake_db, "EMPLOYEE", department_id=DEPT_OWN)

    resp = client.post(
        "/api/recurring-templates",
        headers=auth_header(make_token(user_id)),
        json=_body(submission_mode="DRAFT", department_id=DEPT_OTHER),
    )

    assert resp.status_code == 403


def test_department_manager_can_view_own_department_but_cannot_create(
    client: TestClient, fake_db: FakeClient
) -> None:
    _seed_refs(fake_db)
    manager_id = seed_user(fake_db, "DEPARTMENT_MANAGER", department_id=DEPT_OWN)
    finance_id = seed_user(fake_db, "FINANCE_ADMIN", email="fa@example.com")
    create = client.post(
        "/api/recurring-templates",
        headers=auth_header(make_token(finance_id)),
        json=_body(department_id=DEPT_OWN),
    )
    assert create.status_code == 201, create.text

    token = auth_header(make_token(manager_id))
    listing = client.get("/api/recurring-templates", headers=token)
    denied = client.post("/api/recurring-templates", headers=token, json=_body())

    assert listing.status_code == 200
    assert len(listing.json()) == 1
    assert denied.status_code == 403


def test_finance_admin_updates_active_template(
    client: TestClient, fake_db: FakeClient
) -> None:
    _seed_refs(fake_db)
    user_id = seed_user(fake_db, "FINANCE_ADMIN")
    token = auth_header(make_token(user_id))
    created = client.post("/api/recurring-templates", headers=token, json=_body())
    assert created.status_code == 201, created.text
    template_id = created.json()["id"]

    resp = client.patch(
        f"/api/recurring-templates/{template_id}",
        headers=token,
        json={"amount": 2_000_000, "interval": 2},
    )

    assert resp.status_code == 200, resp.text
    assert resp.json()["amount"] == 2_000_000
    assert resp.json()["interval"] == 2


def test_employee_cannot_update_template_to_auto_submit(
    client: TestClient, fake_db: FakeClient
) -> None:
    _seed_refs(fake_db)
    user_id = seed_user(fake_db, "EMPLOYEE", department_id=DEPT_OWN)
    token = auth_header(make_token(user_id))
    created = client.post("/api/recurring-templates", headers=token, json=_body())
    assert created.status_code == 201, created.text
    template_id = created.json()["id"]

    resp = client.patch(
        f"/api/recurring-templates/{template_id}",
        headers=token,
        json={"submission_mode": "AUTO_SUBMIT"},
    )

    assert resp.status_code == 403


def test_deactivate_sets_inactive_without_deleting(
    client: TestClient, fake_db: FakeClient
) -> None:
    _seed_refs(fake_db)
    user_id = seed_user(fake_db, "FINANCE_ADMIN")
    token = auth_header(make_token(user_id))
    created = client.post("/api/recurring-templates", headers=token, json=_body())
    assert created.status_code == 201, created.text
    template_id = created.json()["id"]

    resp = client.post(
        f"/api/recurring-templates/{template_id}/deactivate", headers=token
    )

    assert resp.status_code == 200, resp.text
    assert resp.json()["is_active"] is False
    assert fake_db.tables["recurring_transaction_templates"][0]["is_active"] is False
