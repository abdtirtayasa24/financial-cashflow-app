import uuid
from collections.abc import Generator
from datetime import UTC, datetime, timedelta
from pathlib import Path

import jwt
import pytest
from app.core.config import Settings, get_settings
from app.core.supabase_client import get_supabase_client
from app.main import app
from fastapi.testclient import TestClient

from tests.fakes import FakeClient

TEST_SECRET = "test-secret"


def make_token(
    sub: str,
    email: str = "user@example.com",
    *,
    expired: bool = False,
) -> str:
    now = datetime.now(UTC)
    exp = now - timedelta(seconds=10) if expired else now + timedelta(hours=1)
    payload = {"sub": sub, "email": email, "exp": exp, "aud": "authenticated"}
    return jwt.encode(payload, TEST_SECRET, algorithm="HS256")


def seed_user(
    db: FakeClient,
    role: str,
    *,
    status: str = "ACTIVE",
    department_id: str | None = None,
    email: str = "user@example.com",
    full_name: str = "Test User",
) -> str:
    user_id = str(uuid.uuid4())
    db.seed(
        "user_profiles",
        [
            {
                "id": user_id,
                "role": role,
                "status": status,
                "department_id": department_id,
                "full_name": full_name,
                "email": email,
                "created_at": "2026-01-01T00:00:00+00:00",
                "updated_at": "2026-01-01T00:00:00+00:00",
            }
        ],
    )
    return user_id


@pytest.fixture
def fake_db() -> FakeClient:
    return FakeClient()


@pytest.fixture(scope="session")
def upload_tmp(tmp_path_factory: pytest.TempPathFactory) -> Path:
    return tmp_path_factory.mktemp("uploads")


@pytest.fixture(autouse=True)
def override_dependencies(
    fake_db: FakeClient, upload_tmp: Path
) -> Generator[None, None, None]:
    app.dependency_overrides[get_supabase_client] = lambda: fake_db
    app.dependency_overrides[get_settings] = lambda: _test_settings(upload_tmp)
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _test_settings(upload_dir: Path) -> Settings:
    return Settings(jwt_secret=TEST_SECRET, upload_dir=str(upload_dir))