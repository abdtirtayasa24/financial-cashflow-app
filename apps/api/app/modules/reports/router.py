from io import BytesIO
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from supabase import Client

from app.core.auth import get_current_user
from app.core.models import CurrentUser
from app.core.supabase_client import get_supabase_client
from app.modules.reports.schemas import (
    CashAccountBalanceOut,
    CategoryBreakdownOut,
    DepartmentBreakdownOut,
    ExportRequest,
    MonthlyTrendOut,
    PendingApprovalsOut,
    ReportFilters,
    SummaryOut,
)
from app.modules.reports.service import ReportService

router = APIRouter(prefix="/reports", tags=["Reports"])

UserDep = Annotated[CurrentUser, Depends(get_current_user)]
DbDep = Annotated[Client, Depends(get_supabase_client)]


def _service(db: Client) -> ReportService:
    return ReportService(db)


def _filters(
    date_from: str | None,
    date_to: str | None,
    department_id: str | None,
    category_id: str | None,
    cash_account_id: str | None,
) -> ReportFilters:
    return ReportFilters(
        date_from=date_from,
        date_to=date_to,
        department_id=department_id,
        category_id=category_id,
        cash_account_id=cash_account_id,
    )


@router.get("/summary", response_model=SummaryOut)
async def summary(
    db: DbDep,
    user: UserDep,
    date_from: Annotated[str | None, Query()] = None,
    date_to: Annotated[str | None, Query()] = None,
    department_id: Annotated[str | None, Query()] = None,
    category_id: Annotated[str | None, Query()] = None,
    cash_account_id: Annotated[str | None, Query()] = None,
) -> SummaryOut:
    return _service(db).summary(
        _filters(date_from, date_to, department_id, category_id, cash_account_id), user
    )


@router.get("/monthly-trend", response_model=list[MonthlyTrendOut])
async def monthly_trend(
    db: DbDep,
    user: UserDep,
    date_from: Annotated[str | None, Query()] = None,
    date_to: Annotated[str | None, Query()] = None,
    department_id: Annotated[str | None, Query()] = None,
    category_id: Annotated[str | None, Query()] = None,
    cash_account_id: Annotated[str | None, Query()] = None,
) -> list[MonthlyTrendOut]:
    return _service(db).monthly_trend(
        _filters(date_from, date_to, department_id, category_id, cash_account_id), user
    )


@router.get("/by-category", response_model=list[CategoryBreakdownOut])
async def by_category(
    db: DbDep,
    user: UserDep,
    date_from: Annotated[str | None, Query()] = None,
    date_to: Annotated[str | None, Query()] = None,
    department_id: Annotated[str | None, Query()] = None,
    category_id: Annotated[str | None, Query()] = None,
    cash_account_id: Annotated[str | None, Query()] = None,
) -> list[CategoryBreakdownOut]:
    return _service(db).by_category(
        _filters(date_from, date_to, department_id, category_id, cash_account_id), user
    )


@router.get("/by-department", response_model=list[DepartmentBreakdownOut])
async def by_department(
    db: DbDep,
    user: UserDep,
    date_from: Annotated[str | None, Query()] = None,
    date_to: Annotated[str | None, Query()] = None,
    department_id: Annotated[str | None, Query()] = None,
    category_id: Annotated[str | None, Query()] = None,
    cash_account_id: Annotated[str | None, Query()] = None,
) -> list[DepartmentBreakdownOut]:
    return _service(db).by_department(
        _filters(date_from, date_to, department_id, category_id, cash_account_id), user
    )


@router.get("/cash-account-balances", response_model=list[CashAccountBalanceOut])
async def cash_account_balances(
    db: DbDep,
    user: UserDep,
    date_from: Annotated[str | None, Query()] = None,
    date_to: Annotated[str | None, Query()] = None,
    department_id: Annotated[str | None, Query()] = None,
    category_id: Annotated[str | None, Query()] = None,
    cash_account_id: Annotated[str | None, Query()] = None,
) -> list[CashAccountBalanceOut]:
    # date_from/date_to are accepted for a common dashboard filter shape, but
    # current cash balances are explicitly as-of now and ignore date range.
    return _service(db).cash_account_balances(
        _filters(None, None, department_id, category_id, cash_account_id), user
    )


@router.get("/pending-approvals", response_model=PendingApprovalsOut)
async def pending_approvals(
    db: DbDep,
    user: UserDep,
    date_from: Annotated[str | None, Query()] = None,
    date_to: Annotated[str | None, Query()] = None,
    department_id: Annotated[str | None, Query()] = None,
) -> PendingApprovalsOut:
    return _service(db).pending_approvals(
        ReportFilters(
            date_from=date_from,
            date_to=date_to,
            department_id=department_id,
        ),
        user,
    )


@router.post("/export")
async def export_report(
    data: ExportRequest,
    db: DbDep,
    user: UserDep,
) -> StreamingResponse:
    body, media_type, filename = _service(db).export(data, user)
    return StreamingResponse(
        BytesIO(body),
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
