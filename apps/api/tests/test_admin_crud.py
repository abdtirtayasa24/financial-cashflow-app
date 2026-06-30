from fastapi.testclient import TestClient

from tests.conftest import auth_header, make_token, seed_user
from tests.fakes import FakeClient


def _admin_token(fake_db: FakeClient) -> str:
    return make_token(seed_user(fake_db, "SYSTEM_ADMIN"))


def test_system_admin_can_list_departments(
    client: TestClient, fake_db: FakeClient
) -> None:
    fake_db.seed(
        "departments",
        [
            {"id": "d1", "name": "Operations", "code": "OPS", "is_active": True,
             "created_at": "2026-01-01T00:00:00+00:00"},
            {"id": "d2", "name": "Finance", "code": "FIN", "is_active": True,
             "created_at": "2026-01-01T00:00:00+00:00"},
        ],
    )
    response = client.get("/api/departments", headers=auth_header(_admin_token(fake_db)))
    assert response.status_code == 200
    names = [d["name"] for d in response.json()]
    assert names == sorted(names)


def test_system_admin_can_create_and_update_department(
    client: TestClient, fake_db: FakeClient
) -> None:
    token = auth_header(_admin_token(fake_db))
    create = client.post(
        "/api/departments",
        headers=token,
        json={"name": "Sales", "code": "SAL"},
    )
    assert create.status_code == 201
    created = create.json()
    assert created["name"] == "Sales"

    update = client.patch(
        f"/api/departments/{created['id']}",
        headers=token,
        json={"is_active": False},
    )
    assert update.status_code == 200
    assert update.json()["is_active"] is False


def test_system_admin_can_manage_cash_account(
    client: TestClient, fake_db: FakeClient
) -> None:
    token = auth_header(_admin_token(fake_db))
    create = client.post(
        "/api/cash-accounts",
        headers=token,
        json={
            "name": "Main Bank",
            "account_type": "BANK",
            "opening_balance": 0,
            "opening_balance_date": "2026-01-01",
        },
    )
    assert create.status_code == 201
    assert create.json()["account_type"] == "BANK"

    listing = client.get("/api/cash-accounts", headers=token)
    assert listing.status_code == 200
    assert len(listing.json()) == 1


def test_system_admin_can_upsert_app_setting(
    client: TestClient, fake_db: FakeClient
) -> None:
    token = auth_header(_admin_token(fake_db))
    first = client.put(
        "/api/settings",
        headers=token,
        json={"key": "attachment_threshold_amount", "value": "5000000"},
    )
    assert first.status_code == 200
    assert first.json()["value"] == "5000000"

    second = client.put(
        "/api/settings",
        headers=token,
        json={"key": "attachment_threshold_amount", "value": "7500000"},
    )
    assert second.status_code == 200
    assert second.json()["value"] == "7500000"
    # Upsert must not duplicate the key.
    assert len(fake_db.tables["app_settings"]) == 1


def test_employee_can_read_departments_but_not_write(
    client: TestClient, fake_db: FakeClient
) -> None:
    user_id = seed_user(fake_db, "EMPLOYEE", department_id="d1")
    token = auth_header(make_token(user_id))
    listing = client.get("/api/departments", headers=token)
    assert listing.status_code == 200
    create = client.post(
        "/api/departments", headers=token, json={"name": "X", "code": "X"}
    )
    assert create.status_code == 403


def test_system_admin_can_list_users(client: TestClient, fake_db: FakeClient) -> None:
    seed_user(fake_db, "EMPLOYEE", email="a@example.com", full_name="A")
    seed_user(fake_db, "FINANCE_ADMIN", email="b@example.com", full_name="B")
    response = client.get("/api/users", headers=auth_header(_admin_token(fake_db)))
    assert response.status_code == 200
    assert len(response.json()) >= 2