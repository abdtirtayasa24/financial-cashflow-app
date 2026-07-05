"""Behavior tests for the recurring transaction generation cron job."""

from __future__ import annotations

import uuid
from datetime import date

from tests.fakes import FakeClient

DEPT_ID = "dept-1"
CAT_ID = "cat-1"
CASH_ID = "cash-1"
PM_ID = "pm-1"
USER_ID = "user-1"


def _seed_reference_data(db: FakeClient) -> None:
    db.seed("departments", [{"id": DEPT_ID, "name": "Finance", "code": "FIN"}])
    db.seed(
        "cashflow_categories",
        [{"id": CAT_ID, "name": "Vendor Payment", "direction": "OUTFLOW"}],
    )
    db.seed("cash_accounts", [{"id": CASH_ID, "name": "Main Bank", "is_active": True}])
    db.seed("payment_methods", [{"id": PM_ID, "name": "Bank Transfer"}])


def seed_template(
    db: FakeClient,
    *,
    template_id: str | None = None,
    submission_mode: str = "DRAFT",
    frequency: str = "MONTHLY",
    interval: int = 1,
    next_run_date: str = "2026-07-01",
    end_date: str | None = None,
    is_active: bool = True,
    direction: str = "OUTFLOW",
    amount: float = 1_000,
    created_by: str = USER_ID,
) -> str:
    tid = template_id or str(uuid.uuid4())
    db.seed(
        "recurring_transaction_templates",
        [
            {
                "id": tid,
                "department_id": DEPT_ID,
                "category_id": CAT_ID,
                "cash_account_id": CASH_ID,
                "payment_method_id": PM_ID,
                "direction": direction,
                "amount": amount,
                "currency": "IDR",
                "counterparty_name": "ACME Corp",
                "reference_no": None,
                "description": "Monthly rent",
                "submission_mode": submission_mode,
                "frequency": frequency,
                "interval": interval,
                "next_run_date": next_run_date,
                "end_date": end_date,
                "is_active": is_active,
                "created_by": created_by,
                "created_at": "2026-01-01T00:00:00+00:00",
                "updated_at": "2026-01-01T00:00:00+00:00",
            }
        ],
    )
    return tid


def seed_user_profile(db: FakeClient) -> str:
    db.seed(
        "user_profiles",
        [
            {
                "id": USER_ID,
                "role": "EMPLOYEE",
                "status": "ACTIVE",
                "department_id": DEPT_ID,
                "full_name": "Test User",
                "email": "user@example.com",
                "created_at": "2026-01-01T00:00:00+00:00",
                "updated_at": "2026-01-01T00:00:00+00:00",
            }
        ],
    )
    return USER_ID


def test_creates_draft_transaction_from_due_draft_mode_template(
    fake_db: FakeClient,
) -> None:
    from app.cron.recurring_generator import RecurringGeneratorService

    _seed_reference_data(fake_db)
    seed_user_profile(fake_db)
    seed_template(
        fake_db, submission_mode="DRAFT", next_run_date="2026-07-01"
    )

    service = RecurringGeneratorService(fake_db)
    result = service.run(today=date(2026, 7, 1))

    txs = fake_db.tables.get("cashflow_transactions", [])
    assert len(txs) == 1
    tx = txs[0]
    assert tx["status"] == "DRAFT"
    assert tx["direction"] == "OUTFLOW"
    assert tx["amount"] == 1_000
    assert tx["transaction_date"] == "2026-07-01"
    assert tx["department_id"] == DEPT_ID
    assert tx["category_id"] == CAT_ID
    assert tx["cash_account_id"] == CASH_ID
    assert tx["payment_method_id"] == PM_ID
    assert tx["created_by"] == USER_ID
    assert tx["currency"] == "IDR"
    assert tx["base_amount"] == 1_000
    assert tx["transaction_no"].startswith("OUTFLOW-202607-")
    assert result.generated == 1


def test_creates_submitted_transaction_from_auto_submit_template(
    fake_db: FakeClient,
) -> None:
    from app.cron.recurring_generator import RecurringGeneratorService

    _seed_reference_data(fake_db)
    seed_user_profile(fake_db)
    # Seed a finance admin so notifications have a target.
    db2 = fake_db
    db2.seed(
        "user_profiles",
        [
            {
                "id": "fa-1",
                "role": "FINANCE_ADMIN",
                "status": "ACTIVE",
                "department_id": None,
                "full_name": "Finance Admin",
                "email": "fa@example.com",
                "created_at": "2026-01-01T00:00:00+00:00",
                "updated_at": "2026-01-01T00:00:00+00:00",
            }
        ],
    )
    seed_template(
        fake_db, submission_mode="AUTO_SUBMIT", next_run_date="2026-07-01"
    )

    service = RecurringGeneratorService(fake_db)
    result = service.run(today=date(2026, 7, 1))

    txs = fake_db.tables.get("cashflow_transactions", [])
    assert len(txs) == 1
    assert txs[0]["status"] == "SUBMITTED"
    assert txs[0]["submitted_at"] is not None
    assert result.generated == 1
    # Audit logs: CREATE + SUBMIT
    logs = fake_db.tables.get("transaction_audit_logs", [])
    actions = [log["action"] for log in logs]
    assert "CREATE" in actions
    assert "SUBMIT" in actions


def test_advances_next_run_date_after_generating(
    fake_db: FakeClient,
) -> None:
    from app.cron.recurring_generator import RecurringGeneratorService

    _seed_reference_data(fake_db)
    seed_user_profile(fake_db)
    seed_template(
        fake_db,
        frequency="MONTHLY",
        interval=1,
        next_run_date="2026-07-01",
    )

    service = RecurringGeneratorService(fake_db)
    service.run(today=date(2026, 7, 1))

    templates = fake_db.tables.get("recurring_transaction_templates", [])
    assert templates[0]["next_run_date"] == "2026-08-01"
    assert templates[0]["is_active"] is True


def test_deactivates_template_when_next_run_exceeds_end_date(
    fake_db: FakeClient,
) -> None:
    from app.cron.recurring_generator import RecurringGeneratorService

    _seed_reference_data(fake_db)
    seed_user_profile(fake_db)
    seed_template(
        fake_db,
        frequency="MONTHLY",
        interval=1,
        next_run_date="2026-07-01",
        end_date="2026-07-31",
    )

    service = RecurringGeneratorService(fake_db)
    service.run(today=date(2026, 7, 1))

    templates = fake_db.tables.get("recurring_transaction_templates", [])
    assert templates[0]["next_run_date"] == "2026-08-01"
    assert templates[0]["is_active"] is False


def test_is_idempotent_running_twice_does_not_duplicate(
    fake_db: FakeClient,
) -> None:
    from app.cron.recurring_generator import RecurringGeneratorService

    _seed_reference_data(fake_db)
    seed_user_profile(fake_db)
    seed_template(fake_db, next_run_date="2026-07-01")

    service = RecurringGeneratorService(fake_db)
    # Simulate an interruption: generate but DON'T advance next_run_date.
    service.run(today=date(2026, 7, 1))
    # Reset next_run_date back to simulate the job being re-run.
    fake_db.tables["recurring_transaction_templates"][0]["next_run_date"] = "2026-07-01"
    service.run(today=date(2026, 7, 1))

    txs = fake_db.tables.get("cashflow_transactions", [])
    assert len(txs) == 1  # no duplicate


def test_idempotent_when_cron_runs_after_next_run_date(
    fake_db: FakeClient,
) -> None:
    """Idempotency guard must use the template's next_run_date (the actual
    transaction_date), not today.  When the cron job runs days after
    next_run_date, re-running must not duplicate."""
    from app.cron.recurring_generator import RecurringGeneratorService

    _seed_reference_data(fake_db)
    seed_user_profile(fake_db)
    seed_template(fake_db, next_run_date="2026-07-01")

    service = RecurringGeneratorService(fake_db)
    # First run: cron executes on July 5, template was due July 1.
    service.run(today=date(2026, 7, 5))
    # Simulate interruption: reset next_run_date back to July 1.
    fake_db.tables["recurring_transaction_templates"][0]["next_run_date"] = "2026-07-01"
    service.run(today=date(2026, 7, 5))

    txs = fake_db.tables.get("cashflow_transactions", [])
    assert len(txs) == 1  # no duplicate — transaction_date is 2026-07-01, not 2026-07-05


def test_notifies_template_creator_for_draft_mode(
    fake_db: FakeClient,
) -> None:
    from app.cron.recurring_generator import RecurringGeneratorService

    _seed_reference_data(fake_db)
    seed_user_profile(fake_db)
    seed_template(fake_db, submission_mode="DRAFT", next_run_date="2026-07-01")

    service = RecurringGeneratorService(fake_db)
    service.run(today=date(2026, 7, 1))

    notifs = fake_db.tables.get("notifications", [])
    assert len(notifs) == 1
    assert notifs[0]["type"] == "RECURRING_DRAFT_READY"
    assert notifs[0]["user_id"] == USER_ID


def test_skips_inactive_templates(
    fake_db: FakeClient,
) -> None:
    from app.cron.recurring_generator import RecurringGeneratorService

    _seed_reference_data(fake_db)
    seed_user_profile(fake_db)
    seed_template(fake_db, is_active=False, next_run_date="2026-07-01")

    service = RecurringGeneratorService(fake_db)
    result = service.run(today=date(2026, 7, 1))

    assert result.generated == 0
    assert len(fake_db.tables.get("cashflow_transactions", [])) == 0


def test_skips_templates_with_end_date_before_today(
    fake_db: FakeClient,
) -> None:
    from app.cron.recurring_generator import RecurringGeneratorService

    _seed_reference_data(fake_db)
    seed_user_profile(fake_db)
    seed_template(
        fake_db, next_run_date="2026-07-01", end_date="2026-06-30"
    )

    service = RecurringGeneratorService(fake_db)
    result = service.run(today=date(2026, 7, 15))

    assert result.generated == 0


def test_weekly_interval_advances_correctly(
    fake_db: FakeClient,
) -> None:
    from app.cron.recurring_generator import RecurringGeneratorService

    _seed_reference_data(fake_db)
    seed_user_profile(fake_db)
    seed_template(
        fake_db, frequency="WEEKLY", interval=2, next_run_date="2026-07-01"
    )

    service = RecurringGeneratorService(fake_db)
    service.run(today=date(2026, 7, 1))

    templates = fake_db.tables.get("recurring_transaction_templates", [])
    assert templates[0]["next_run_date"] == "2026-07-15"