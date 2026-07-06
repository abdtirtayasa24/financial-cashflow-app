"""Behavior tests for attachment-threshold app settings."""

from __future__ import annotations

from fastapi.testclient import TestClient

from tests.conftest import auth_header, make_token, seed_user
from tests.fakes import FakeClient


def test_system_admin_updates_attachment_threshold_settings(
    client: TestClient, fake_db: FakeClient
) -> None:
    user_id = seed_user(fake_db, "SYSTEM_ADMIN")
    token = auth_header(make_token(user_id))

    enabled = client.put(
        "/api/settings",
        headers=token,
        json={"key": "attachment_threshold_enabled", "value": "false"},
    )
    amount = client.put(
        "/api/settings",
        headers=token,
        json={"key": "attachment_threshold_amount", "value": "7500000"},
    )

    assert enabled.status_code == 200, enabled.text
    assert enabled.json()["value"] == "false"
    assert amount.status_code == 200, amount.text
    assert amount.json()["value"] == "7500000"


def test_management_updates_attachment_threshold_settings(
    client: TestClient, fake_db: FakeClient
) -> None:
    user_id = seed_user(fake_db, "MANAGEMENT")

    resp = client.put(
        "/api/settings",
        headers=auth_header(make_token(user_id)),
        json={"key": "attachment_threshold_amount", "value": "8000000"},
    )

    assert resp.status_code == 200, resp.text
    assert resp.json()["value"] == "8000000"


def test_attachment_threshold_enabled_must_be_boolean(
    client: TestClient, fake_db: FakeClient
) -> None:
    user_id = seed_user(fake_db, "SYSTEM_ADMIN")

    resp = client.put(
        "/api/settings",
        headers=auth_header(make_token(user_id)),
        json={"key": "attachment_threshold_enabled", "value": "maybe"},
    )

    assert resp.status_code == 422


def test_attachment_threshold_amount_must_be_positive_number(
    client: TestClient, fake_db: FakeClient
) -> None:
    user_id = seed_user(fake_db, "SYSTEM_ADMIN")

    resp = client.put(
        "/api/settings",
        headers=auth_header(make_token(user_id)),
        json={"key": "attachment_threshold_amount", "value": "-1"},
    )

    assert resp.status_code == 422
