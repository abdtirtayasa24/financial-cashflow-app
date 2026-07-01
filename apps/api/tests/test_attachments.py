"""Behavior tests for transaction attachments (VPS local storage)."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from tests.conftest import auth_header, make_token, seed_user
from tests.fakes import FakeClient
from tests.test_transactions import seed_transaction

DEPT_OWN = "dept-own"


def _pdf(name: str = "receipt.pdf") -> tuple[str, bytes, str]:
    return (name, b"%PDF-1.4 test content", "application/pdf")


def test_upload_pdf_succeeds_and_writes_file(
    client: TestClient, fake_db: FakeClient, upload_tmp: Path
) -> None:
    fin_id = seed_user(fake_db, "FINANCE_ADMIN")
    tx_id = seed_transaction(fake_db, created_by=fin_id)
    resp = client.post(
        f"/api/transactions/{tx_id}/attachments",
        headers=auth_header(make_token(fin_id)),
        files={"file": _pdf()},
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["original_file_name"] == "receipt.pdf"
    assert body["mime_type"] == "application/pdf"
    assert body["checksum_sha256"]
    # File exists on VPS local storage.
    assert (upload_tmp / body["relative_path"]).exists()
    # ATTACHMENT_ADD audit log recorded.
    assert any(lg["action"] == "ATTACHMENT_ADD"
               for lg in fake_db.tables["transaction_audit_logs"])


def test_upload_rejects_invalid_type(
    client: TestClient, fake_db: FakeClient
) -> None:
    fin_id = seed_user(fake_db, "FINANCE_ADMIN")
    tx_id = seed_transaction(fake_db, created_by=fin_id)
    resp = client.post(
        f"/api/transactions/{tx_id}/attachments",
        headers=auth_header(make_token(fin_id)),
        files={"file": ("notes.txt", b"hello", "text/plain")},
    )
    assert resp.status_code == 400
    assert "not allowed" in resp.json()["detail"]


def test_upload_rejects_oversize(
    client: TestClient, fake_db: FakeClient
) -> None:
    fin_id = seed_user(fake_db, "FINANCE_ADMIN")
    tx_id = seed_transaction(fake_db, created_by=fin_id)
    too_big = b"0" * (10 * 1024 * 1024 + 1)
    resp = client.post(
        f"/api/transactions/{tx_id}/attachments",
        headers=auth_header(make_token(fin_id)),
        files={"file": ("big.pdf", too_big, "application/pdf")},
    )
    assert resp.status_code == 413


def test_upload_only_while_mutable(
    client: TestClient, fake_db: FakeClient
) -> None:
    fin_id = seed_user(fake_db, "FINANCE_ADMIN")
    tx_id = seed_transaction(fake_db, created_by=fin_id, status="APPROVED")
    resp = client.post(
        f"/api/transactions/{tx_id}/attachments",
        headers=auth_header(make_token(fin_id)),
        files={"file": _pdf()},
    )
    assert resp.status_code == 409


def test_employee_cannot_upload_to_others_transaction(
    client: TestClient, fake_db: FakeClient
) -> None:
    emp_id = seed_user(fake_db, "EMPLOYEE", department_id=DEPT_OWN)
    other_id = seed_user(
        fake_db, "EMPLOYEE", department_id=DEPT_OWN, email="o@x.com", full_name="O"
    )
    tx_id = seed_transaction(fake_db, created_by=other_id)
    resp = client.post(
        f"/api/transactions/{tx_id}/attachments",
        headers=auth_header(make_token(emp_id)),
        files={"file": _pdf()},
    )
    assert resp.status_code == 403


def test_list_attachments_requires_view(
    client: TestClient, fake_db: FakeClient
) -> None:
    fin_id = seed_user(fake_db, "FINANCE_ADMIN")
    tx_id = seed_transaction(fake_db, created_by=fin_id)
    resp = client.get(
        f"/api/transactions/{tx_id}/attachments",
        headers=auth_header(make_token(fin_id)),
    )
    assert resp.status_code == 200
    assert resp.json() == []


def test_download_streams_file(
    client: TestClient, fake_db: FakeClient, upload_tmp: Path
) -> None:
    fin_id = seed_user(fake_db, "FINANCE_ADMIN")
    tx_id = seed_transaction(fake_db, created_by=fin_id)
    uploaded = client.post(
        f"/api/transactions/{tx_id}/attachments",
        headers=auth_header(make_token(fin_id)),
        files={"file": _pdf("doc.pdf")},
    ).json()
    resp = client.get(
        f"/api/transactions/{tx_id}/attachments/{uploaded['id']}/download",
        headers=auth_header(make_token(fin_id)),
    )
    assert resp.status_code == 200
    assert b"%PDF" in resp.content


def test_download_requires_view_permission(
    client: TestClient, fake_db: FakeClient, upload_tmp: Path
) -> None:
    fin_id = seed_user(fake_db, "FINANCE_ADMIN")
    other_emp = seed_user(
        fake_db, "EMPLOYEE", department_id="dept-other", email="o@x.com", full_name="O"
    )
    tx_id = seed_transaction(fake_db, created_by=fin_id, department_id="dept-other")
    uploaded = client.post(
        f"/api/transactions/{tx_id}/attachments",
        headers=auth_header(make_token(fin_id)),
        files={"file": _pdf()},
    ).json()
    # other_emp is in a different department and did not create the transaction.
    resp = client.get(
        f"/api/transactions/{tx_id}/attachments/{uploaded['id']}/download",
        headers=auth_header(make_token(other_emp)),
    )
    assert resp.status_code == 404


def test_delete_attachment_removes_file(
    client: TestClient, fake_db: FakeClient, upload_tmp: Path
) -> None:
    fin_id = seed_user(fake_db, "FINANCE_ADMIN")
    tx_id = seed_transaction(fake_db, created_by=fin_id)
    uploaded = client.post(
        f"/api/transactions/{tx_id}/attachments",
        headers=auth_header(make_token(fin_id)),
        files={"file": _pdf()},
    ).json()
    file_path = upload_tmp / uploaded["relative_path"]
    assert file_path.exists()

    resp = client.delete(
        f"/api/transactions/{tx_id}/attachments/{uploaded['id']}",
        headers=auth_header(make_token(fin_id)),
    )
    assert resp.status_code == 204
    assert not file_path.exists()
    assert not any(a["id"] == uploaded["id"]
                   for a in fake_db.tables.get("transaction_attachments", []))
    assert any(lg["action"] == "ATTACHMENT_REMOVE"
               for lg in fake_db.tables["transaction_audit_logs"])


# ── review-fix regressions ─────────────────────────────────────


def test_delete_attachment_from_other_transaction_remains(
    client: TestClient, fake_db: FakeClient, upload_tmp: Path
) -> None:
    fin_id = seed_user(fake_db, "FINANCE_ADMIN")
    tx_a = seed_transaction(
        fake_db, created_by=fin_id, transaction_id="tx-a",
        transaction_no="INFLOW-202607-000001",
    )
    tx_b = seed_transaction(
        fake_db, created_by=fin_id, transaction_id="tx-b",
        transaction_no="OUTFLOW-202607-000001",
    )
    # Upload an attachment that belongs to tx_b.
    uploaded = client.post(
        f"/api/transactions/{tx_b}/attachments",
        headers=auth_header(make_token(fin_id)),
        files={"file": _pdf("b.pdf")},
    ).json()

    # Finance Admin can mutate tx_a, but the attachment belongs to tx_b.
    # The delete must be rejected and the attachment metadata preserved.
    resp = client.delete(
        f"/api/transactions/{tx_a}/attachments/{uploaded['id']}",
        headers=auth_header(make_token(fin_id)),
    )
    assert resp.status_code == 404
    assert any(a["id"] == uploaded["id"]
               for a in fake_db.tables["transaction_attachments"])


def test_upload_rejects_mismatched_content_and_magic(
    client: TestClient, fake_db: FakeClient
) -> None:
    fin_id = seed_user(fake_db, "FINANCE_ADMIN")
    tx_id = seed_transaction(fake_db, created_by=fin_id)
    token = auth_header(make_token(fin_id))

    # Extension says PDF but declared content type is text/plain.
    wrong_type = client.post(
        f"/api/transactions/{tx_id}/attachments",
        headers=token,
        files={"file": ("doc.pdf", b"%PDF-1.4 ok", "text/plain")},
    )
    assert wrong_type.status_code == 400

    # Declared content type is PDF but the bytes are not a real PDF.
    wrong_magic = client.post(
        f"/api/transactions/{tx_id}/attachments",
        headers=token,
        files={"file": ("doc.pdf", b"not actually a pdf", "application/pdf")},
    )
    assert wrong_magic.status_code == 400