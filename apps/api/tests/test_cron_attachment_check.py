"""Behavior tests for missing attachment check cron job."""

from __future__ import annotations

import logging

import pytest

from tests.fakes import FakeClient


def _seed_threshold(
    db: FakeClient, enabled: str = "true", amount: str = "5000000"
) -> None:
    db.seed("app_settings", [
        {"id": "s1", "key": "attachment_threshold_enabled", "value": enabled},
        {"id": "s2", "key": "attachment_threshold_amount", "value": amount},
    ])


def _seed_submitted_tx(
    db: FakeClient,
    *,
    tx_id: str = "tx-1",
    amount: float = 6_000_000,
    transaction_no: str = "OUTFLOW-202607-000001",
) -> None:
    db.seed("cashflow_transactions", [
        {
            "id": tx_id,
            "transaction_no": transaction_no,
            "transaction_date": "2026-07-10",
            "direction": "OUTFLOW",
            "amount": amount,
            "currency": "IDR",
            "exchange_rate": 1,
            "base_amount": amount,
            "cash_account_id": "ca-1",
            "department_id": "d-1",
            "category_id": "c-1",
            "payment_method_id": "pm-1",
            "counterparty_name": None,
            "reference_no": None,
            "description": None,
            "status": "SUBMITTED",
            "created_by": "u-1",
            "submitted_at": "2026-07-10T00:00:00+00:00",
            "reviewed_by": None,
            "reviewed_at": None,
            "rejection_reason": None,
            "void_reason": None,
            "created_at": "2026-07-10T00:00:00+00:00",
            "updated_at": "2026-07-10T00:00:00+00:00",
        }
    ])


def test_exits_early_when_threshold_disabled(fake_db: FakeClient) -> None:
    from app.cron.attachment_check import AttachmentCheckService

    _seed_threshold(fake_db, enabled="false")
    _seed_submitted_tx(fake_db)

    service = AttachmentCheckService(fake_db)
    result = service.run()

    assert result.checked == 0
    assert result.flagged == 0


def test_flags_submitted_transaction_above_threshold_without_attachments(
    fake_db: FakeClient, caplog: pytest.LogCaptureFixture
) -> None:
    from app.cron.attachment_check import AttachmentCheckService

    _seed_threshold(fake_db)
    _seed_submitted_tx(fake_db, tx_id="tx-1", amount=6_000_000)

    service = AttachmentCheckService(fake_db)
    with caplog.at_level(logging.WARNING):
        result = service.run()

    assert result.checked == 1
    assert result.flagged == 1
    assert any("tx-1" in r.message or "OUTFLOW-202607-000001" in r.message
               for r in caplog.records)


def test_does_not_flag_transaction_with_attachments(fake_db: FakeClient) -> None:
    from app.cron.attachment_check import AttachmentCheckService

    _seed_threshold(fake_db)
    _seed_submitted_tx(fake_db, tx_id="tx-1", amount=6_000_000)
    fake_db.seed("transaction_attachments", [
        {
            "id": "att-1",
            "transaction_id": "tx-1",
            "original_file_name": "receipt.pdf",
            "stored_file_name": "uuid.pdf",
            "relative_path": "2026/07/tx-1/uuid.pdf",
            "mime_type": "application/pdf",
            "file_size_bytes": 1024,
            "checksum_sha256": None,
            "uploaded_by": "u-1",
            "uploaded_at": "2026-07-10T00:00:00+00:00",
        }
    ])

    service = AttachmentCheckService(fake_db)
    result = service.run()

    assert result.checked == 1
    assert result.flagged == 0


def test_does_not_flag_transaction_below_threshold(fake_db: FakeClient) -> None:
    from app.cron.attachment_check import AttachmentCheckService

    _seed_threshold(fake_db)
    _seed_submitted_tx(fake_db, tx_id="tx-1", amount=3_000_000)

    service = AttachmentCheckService(fake_db)
    result = service.run()

    assert result.checked == 1
    assert result.flagged == 0


def test_is_read_only_does_not_modify_transactions(fake_db: FakeClient) -> None:
    from app.cron.attachment_check import AttachmentCheckService

    _seed_threshold(fake_db)
    _seed_submitted_tx(fake_db, tx_id="tx-1")

    original_status = fake_db.tables["cashflow_transactions"][0]["status"]
    service = AttachmentCheckService(fake_db)
    service.run()

    assert fake_db.tables["cashflow_transactions"][0]["status"] == original_status


def test_rerun_produces_same_result(fake_db: FakeClient) -> None:
    from app.cron.attachment_check import AttachmentCheckService

    _seed_threshold(fake_db)
    _seed_submitted_tx(fake_db, tx_id="tx-1")

    service = AttachmentCheckService(fake_db)
    first = service.run()
    second = service.run()

    assert first == second