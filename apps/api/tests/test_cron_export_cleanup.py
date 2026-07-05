"""Behavior tests for export cleanup cron job."""

from __future__ import annotations

import os
import time
from pathlib import Path

from tests.fakes import FakeClient


def test_deletes_files_older_than_retention_period(tmp_path: Path) -> None:
    from app.cron.export_cleanup import ExportCleanupService

    db = FakeClient()
    db.seed("app_settings", [{"id": "s1", "key": "export_retention_days", "value": "7"}])
    exports_dir = tmp_path / "exports"
    exports_dir.mkdir()
    old_file = exports_dir / "old-report.xlsx"
    old_file.write_bytes(b"old")
    new_file = exports_dir / "new-report.xlsx"
    new_file.write_bytes(b"new")
    # Set old_file's modification time to 10 days ago.
    old_time = time.time() - (10 * 86400)
    os.utime(old_file, (old_time, old_time))

    service = ExportCleanupService(db, exports_dir=str(exports_dir))
    deleted = service.run()

    assert deleted == 1
    assert not old_file.exists()
    assert new_file.exists()


def test_safe_noop_when_directory_does_not_exist(tmp_path: Path) -> None:
    from app.cron.export_cleanup import ExportCleanupService

    db = FakeClient()
    db.seed("app_settings", [{"id": "s1", "key": "export_retention_days", "value": "7"}])
    missing_dir = tmp_path / "nonexistent"

    service = ExportCleanupService(db, exports_dir=str(missing_dir))
    deleted = service.run()

    assert deleted == 0


def test_uses_default_retention_when_setting_missing(tmp_path: Path) -> None:
    from app.cron.export_cleanup import ExportCleanupService

    db = FakeClient()
    # No export_retention_days setting in app_settings.
    exports_dir = tmp_path / "exports"
    exports_dir.mkdir()
    # File 10 days old — default retention is 7 days, so should be deleted.
    old_file = exports_dir / "old.xlsx"
    old_file.write_bytes(b"old")
    old_time = time.time() - (10 * 86400)
    os.utime(old_file, (old_time, old_time))

    service = ExportCleanupService(db, exports_dir=str(exports_dir))
    deleted = service.run()

    assert deleted == 1


def test_empty_directory_is_safe_noop(tmp_path: Path) -> None:
    from app.cron.export_cleanup import ExportCleanupService

    db = FakeClient()
    db.seed("app_settings", [{"id": "s1", "key": "export_retention_days", "value": "7"}])
    exports_dir = tmp_path / "exports"
    exports_dir.mkdir()

    service = ExportCleanupService(db, exports_dir=str(exports_dir))
    deleted = service.run()

    assert deleted == 0