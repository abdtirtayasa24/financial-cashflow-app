"""Behavior tests for externally triggered cron jobs."""

from __future__ import annotations

import os
import time
from pathlib import Path

from app.core.config import Settings, get_settings
from app.main import app
from fastapi.testclient import TestClient


def _cron_settings(exports_dir: Path) -> Settings:
    return Settings(
        jwt_secret="test-secret",
        cron_api_token="cron-secret",
        exports_dir=str(exports_dir),
    )


def test_cron_api_rejects_missing_or_invalid_token(
    client: TestClient, tmp_path: Path
) -> None:
    app.dependency_overrides[get_settings] = lambda: _cron_settings(tmp_path)

    missing = client.post("/api/cron/jobs/check-missing-attachments/run")
    invalid = client.post(
        "/api/cron/jobs/check-missing-attachments/run",
        headers={"Authorization": "Bearer wrong"},
    )

    assert missing.status_code == 401
    assert invalid.status_code == 403


def test_cron_api_returns_503_when_token_unconfigured(
    client: TestClient, tmp_path: Path
) -> None:
    app.dependency_overrides[get_settings] = lambda: Settings(
        jwt_secret="test-secret",
        cron_api_token="",
        exports_dir=str(tmp_path),
    )

    resp = client.post(
        "/api/cron/jobs/cleanup-old-exports/run",
        headers={"Authorization": "Bearer anything"},
    )

    assert resp.status_code == 503


def test_cron_api_runs_cleanup_old_exports_job(
    client: TestClient, tmp_path: Path
) -> None:
    app.dependency_overrides[get_settings] = lambda: _cron_settings(tmp_path)
    expired = tmp_path / "expired.csv"
    fresh = tmp_path / "fresh.csv"
    expired.write_text("old")
    fresh.write_text("new")
    old_time = time.time() - (8 * 86400)
    os.utime(expired, (old_time, old_time))

    resp = client.post(
        "/api/cron/jobs/cleanup-old-exports/run",
        headers={"Authorization": "Bearer cron-secret"},
    )

    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body == {
        "job": "cleanup-old-exports",
        "status": "ok",
        "result": {"deleted": 1},
    }
    assert not expired.exists()
    assert fresh.exists()
