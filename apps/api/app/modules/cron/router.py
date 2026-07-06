from __future__ import annotations

import hmac
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Header, HTTPException, status
from supabase import Client

from app.core.config import Settings, get_settings
from app.core.supabase_client import get_supabase_client
from app.cron.attachment_check import AttachmentCheckService
from app.cron.export_cleanup import ExportCleanupService
from app.cron.recurring_generator import RecurringGeneratorService
from app.cron.report_snapshot import ReportSnapshotService

router = APIRouter(prefix="/cron", tags=["Cron"])


@router.post("/jobs/{job_name}/run")
def run_cron_job(
    job_name: str,
    db: Annotated[Client, Depends(get_supabase_client)],
    settings: Annotated[Settings, Depends(get_settings)],
    authorization: Annotated[str | None, Header()] = None,
) -> dict[str, Any]:
    _require_cron_token(authorization, settings)
    result = _run_job(job_name, db, settings)
    return {"job": job_name, "status": "ok", "result": result}


def _require_cron_token(authorization: str | None, settings: Settings) -> None:
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="missing token",
        )
    prefix = "Bearer "
    if not authorization.startswith(prefix):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="missing token",
        )
    token = authorization[len(prefix) :]
    expected = settings.cron_api_token
    if not expected:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="cron api token is not configured",
        )
    if not hmac.compare_digest(token, expected):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden")


def _run_job(job_name: str, db: Client, settings: Settings) -> dict[str, Any]:
    if job_name == "refresh-report-snapshots":
        ReportSnapshotService(db).daily_snapshot()
        return {"snapshots_refreshed": 1}
    if job_name == "monthly-financial-snapshot":
        ReportSnapshotService(db).monthly_snapshot()
        return {"snapshots_refreshed": 1}
    if job_name == "cleanup-old-exports":
        deleted = ExportCleanupService(db, exports_dir=settings.exports_dir).run()
        return {"deleted": deleted}
    if job_name == "check-missing-attachments":
        attachment_result = AttachmentCheckService(db).run()
        return {
            "checked": attachment_result.checked,
            "flagged": attachment_result.flagged,
        }
    if job_name == "generate-recurring-transactions":
        generation_result = RecurringGeneratorService(db).run()
        return {
            "generated": generation_result.generated,
            "skipped": generation_result.skipped,
            "errors": generation_result.errors,
        }
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="unknown cron job")
