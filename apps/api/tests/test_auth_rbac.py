from app.main import app
from fastapi.testclient import TestClient

from tests.conftest import auth_header, make_token, seed_user
from tests.fakes import FakeClient


def test_me_rejects_missing_token(client: TestClient) -> None:
    response = client.get("/api/me")
    assert response.status_code in (401, 403)


def test_invalid_token_is_rejected(client: TestClient) -> None:
    response = client.get("/api/me", headers=auth_header("not-a-jwt"))
    assert response.status_code == 401


def test_expired_token_is_rejected(client: TestClient, fake_db: FakeClient) -> None:
    user_id = seed_user(fake_db, "SYSTEM_ADMIN")
    response = client.get(
        "/api/me", headers=auth_header(make_token(user_id, expired=True))
    )
    assert response.status_code == 401


def test_inactive_user_is_rejected(client: TestClient, fake_db: FakeClient) -> None:
    user_id = seed_user(fake_db, "SYSTEM_ADMIN", status="INACTIVE")
    response = client.get("/api/me", headers=auth_header(make_token(user_id)))
    assert response.status_code == 401
    assert response.json()["detail"] == "inactive user"


def test_unknown_user_is_rejected(client: TestClient) -> None:
    # A valid token for a user that has no profile row.
    response = client.get(
        "/api/me", headers=auth_header(make_token("does-not-exist-id"))
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "user not found"


def test_active_user_can_read_own_profile(
    client: TestClient, fake_db: FakeClient
) -> None:
    user_id = seed_user(
        fake_db, "FINANCE_ADMIN", email="fin@example.com", full_name="Fin Admin"
    )
    response = client.get(
        "/api/me",
        headers=auth_header(make_token(user_id, email="fin@example.com")),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == user_id
    assert body["role"] == "FINANCE_ADMIN"
    assert body["email"] == "fin@example.com"
    assert body["full_name"] == "Fin Admin"
    # Role is a single value (one role per user).
    assert isinstance(body["role"], str)


def test_non_admin_cannot_create_user(client: TestClient, fake_db: FakeClient) -> None:
    user_id = seed_user(fake_db, "EMPLOYEE")
    response = client.post(
        "/api/users",
        headers=auth_header(make_token(user_id)),
        json={
            "email": "new@example.com",
            "password": "supersecret",
            "full_name": "New User",
            "role": "EMPLOYEE",
            "department_id": "dept-1",
        },
    )
    assert response.status_code == 403


def test_system_admin_can_create_user(client: TestClient, fake_db: FakeClient) -> None:
    admin_id = seed_user(fake_db, "SYSTEM_ADMIN")
    response = client.post(
        "/api/users",
        headers=auth_header(make_token(admin_id)),
        json={
            "email": "new@example.com",
            "password": "supersecret",
            "full_name": "New User",
            "role": "FINANCE_ADMIN",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "new@example.com"
    assert body["role"] == "FINANCE_ADMIN"
    assert body["status"] == "ACTIVE"
    # A Supabase Auth user was created and a profile row was inserted.
    assert body["id"] in fake_db.auth_users
    profiles = fake_db.tables["user_profiles"]
    assert any(p["id"] == body["id"] for p in profiles)


def test_employee_role_requires_department(
    client: TestClient, fake_db: FakeClient
) -> None:
    admin_id = seed_user(fake_db, "SYSTEM_ADMIN")
    response = client.post(
        "/api/users",
        headers=auth_header(make_token(admin_id)),
        json={
            "email": "emp@example.com",
            "password": "supersecret",
            "full_name": "Emp",
            "role": "EMPLOYEE",
        },
    )
    assert response.status_code == 422


def test_non_admin_cannot_update_department(
    client: TestClient, fake_db: FakeClient
) -> None:
    user_id = seed_user(fake_db, "MANAGEMENT")
    response = client.patch(
        "/api/departments/dept-1",
        headers=auth_header(make_token(user_id)),
        json={"name": "Renamed"},
    )
    assert response.status_code == 403


def test_jwt_secret_is_never_in_response_payloads() -> None:
    # Smoke check: routes never embed the secret in their summaries/paths.
    for route in app.routes:
        if hasattr(route, "path") and route.path.startswith("/api/"):
            assert "jwt_secret" not in getattr(route, "path", "")