"""Behavior tests for report snapshot cron jobs."""

from __future__ import annotations

from datetime import date

from tests.fakes import FakeClient


def seed_report_rows(db: FakeClient) -> None:
    db.seed(
        "approved_cashflow_report_base",
        [
            {
                "id": "r1",
                "transaction_no": "INFLOW-202607-000001",
                "transaction_date": "2026-07-10",
                "direction": "INFLOW",
                "amount": 1_000,
                "base_amount": 1_000,
                "currency": "IDR",
                "cash_account_id": "ca-1",
                "cash_account_name": "Main Bank",
                "department_id": "d-1",
                "department_name": "Finance",
                "department_code": "FIN",
                "category_id": "c-1",
                "category_name": "Sales Income",
                "payment_method_id": "pm-1",
                "payment_method_name": "Cash",
                "counterparty_name": None,
                "reference_no": None,
                "description": None,
                "status": "APPROVED",
                "reviewed_at": "2026-07-01T00:00:00+00:00",
            },
            {
                "id": "r2",
                "transaction_no": "OUTFLOW-202607-000001",
                "transaction_date": "2026-07-11",
                "direction": "OUTFLOW",
                "amount": 250,
                "base_amount": 250,
                "currency": "IDR",
                "cash_account_id": "ca-1",
                "cash_account_name": "Main Bank",
                "department_id": "d-1",
                "department_name": "Finance",
                "department_code": "FIN",
                "category_id": "c-2",
                "category_name": "Vendor Payment",
                "payment_method_id": "pm-1",
                "payment_method_name": "Cash",
                "counterparty_name": None,
                "reference_no": None,
                "description": None,
                "status": "APPROVED",
                "reviewed_at": "2026-07-01T00:00:00+00:00",
            },
        ],
    )
    db.seed(
        "cash_accounts",
        [
            {
                "id": "ca-1",
                "name": "Main Bank",
                "account_type": "BANK",
                "opening_balance": 500,
                "opening_balance_date": "2026-01-01",
                "currency": "IDR",
                "is_active": True,
            }
        ],
    )


def test_daily_snapshot_stores_summary_data(fake_db: FakeClient) -> None:
    from app.cron.report_snapshot import ReportSnapshotService

    seed_report_rows(fake_db)

    service = ReportSnapshotService(fake_db)
    service.daily_snapshot(today=date(2026, 7, 15))

    snapshots = fake_db.tables.get("report_snapshots", [])
    assert len(snapshots) == 1
    snap = snapshots[0]
    assert snap["report_type"] == "daily_summary"
    assert snap["date_from"] == "2026-07-15"
    assert snap["date_to"] == "2026-07-15"
    result = snap["result"]
    assert result["summary"]["totalInflow"] == 1000.0
    assert result["summary"]["totalOutflow"] == 250.0
    assert result["summary"]["netCashflow"] == 750.0


def test_daily_snapshot_is_idempotent_no_duplicate_on_rerun(
    fake_db: FakeClient,
) -> None:
    from app.cron.report_snapshot import ReportSnapshotService

    seed_report_rows(fake_db)

    service = ReportSnapshotService(fake_db)
    service.daily_snapshot(today=date(2026, 7, 15))
    service.daily_snapshot(today=date(2026, 7, 15))

    snapshots = fake_db.tables.get("report_snapshots", [])
    assert len(snapshots) == 1


def test_monthly_snapshot_covers_previous_month(fake_db: FakeClient) -> None:
    from app.cron.report_snapshot import ReportSnapshotService

    seed_report_rows(fake_db)

    service = ReportSnapshotService(fake_db)
    service.monthly_snapshot(today=date(2026, 8, 1))

    snapshots = fake_db.tables.get("report_snapshots", [])
    assert len(snapshots) == 1
    snap = snapshots[0]
    assert snap["report_type"] == "monthly_summary"
    assert snap["date_from"] == "2026-07-01"
    assert snap["date_to"] == "2026-07-31"
    result = snap["result"]
    assert result["summary"]["totalInflow"] == 1000.0
    assert result["summary"]["totalOutflow"] == 250.0


def test_monthly_snapshot_is_idempotent(fake_db: FakeClient) -> None:
    from app.cron.report_snapshot import ReportSnapshotService

    seed_report_rows(fake_db)

    service = ReportSnapshotService(fake_db)
    service.monthly_snapshot(today=date(2026, 8, 1))
    service.monthly_snapshot(today=date(2026, 8, 1))

    snapshots = fake_db.tables.get("report_snapshots", [])
    assert len(snapshots) == 1