from collections.abc import Iterable
from io import BytesIO
from typing import Any

from openpyxl import Workbook  # type: ignore[import-untyped]
from reportlab.lib import colors  # type: ignore[import-untyped]
from reportlab.lib.pagesizes import A4  # type: ignore[import-untyped]
from reportlab.platypus import (  # type: ignore[import-untyped]
    SimpleDocTemplate,
    Table,
    TableStyle,
)
from supabase import Client

from app.core.errors import AppError
from app.core.models import CurrentUser, Role, UserStatus
from app.modules.reports.repository import ReportRepository, Rows
from app.modules.reports.schemas import (
    CashAccountBalanceOut,
    CategoryBreakdownOut,
    DepartmentBreakdownOut,
    ExportFormat,
    ExportRequest,
    MonthlyTrendOut,
    PendingApprovalsOut,
    ReportFilters,
    ReportType,
    SummaryOut,
)

_REPORT_ROLES = {Role.FINANCE_ADMIN, Role.MANAGEMENT}


def _amount(row: dict[str, Any]) -> float:
    return float(row.get("base_amount") or 0)


class ReportService:
    def __init__(self, db: Client) -> None:
        self.repo = ReportRepository(db)

    def _require_access(self, user: CurrentUser) -> None:
        if user.role not in _REPORT_ROLES:
            raise AppError("forbidden", 403)

    def summary(self, filters: ReportFilters, user: CurrentUser) -> SummaryOut:
        self._require_access(user)
        return self._summary_from_rows(self.repo.approved_rows(filters))

    def monthly_trend(
        self, filters: ReportFilters, user: CurrentUser
    ) -> list[MonthlyTrendOut]:
        self._require_access(user)
        grouped: dict[str, dict[str, float]] = {}
        for row in self.repo.approved_rows(filters):
            month = str(row["transaction_date"])[:7]
            item = grouped.setdefault(month, {"inflow": 0.0, "outflow": 0.0})
            if row["direction"] == "INFLOW":
                item["inflow"] += _amount(row)
            else:
                item["outflow"] += _amount(row)
        return [
            MonthlyTrendOut(
                month=month,
                inflow=values["inflow"],
                outflow=values["outflow"],
                net=values["inflow"] - values["outflow"],
            )
            for month, values in sorted(grouped.items())
        ]

    def by_category(
        self, filters: ReportFilters, user: CurrentUser
    ) -> list[CategoryBreakdownOut]:
        self._require_access(user)
        grouped: dict[tuple[str, str, str], float] = {}
        for row in self.repo.approved_rows(filters):
            key = (row["category_id"], row["category_name"], row["direction"])
            grouped[key] = grouped.get(key, 0.0) + _amount(row)
        return [
            CategoryBreakdownOut(
                category_id=category_id,
                category_name=category_name,
                direction=direction,
                amount=amount,
            )
            for (category_id, category_name, direction), amount in sorted(
                grouped.items(), key=lambda item: (item[0][1], item[0][2])
            )
        ]

    def by_department(
        self, filters: ReportFilters, user: CurrentUser
    ) -> list[DepartmentBreakdownOut]:
        self._require_access(user)
        grouped: dict[tuple[str, str], dict[str, float]] = {}
        for row in self.repo.approved_rows(filters):
            key = (row["department_id"], row["department_name"])
            item = grouped.setdefault(key, {"inflow": 0.0, "outflow": 0.0})
            if row["direction"] == "INFLOW":
                item["inflow"] += _amount(row)
            else:
                item["outflow"] += _amount(row)
        return [
            DepartmentBreakdownOut(
                department_id=department_id,
                department_name=department_name,
                inflow=values["inflow"],
                outflow=values["outflow"],
                net=values["inflow"] - values["outflow"],
            )
            for (department_id, department_name), values in sorted(
                grouped.items(), key=lambda item: item[0][1]
            )
        ]

    def cash_account_balances(
        self, filters: ReportFilters, user: CurrentUser
    ) -> list[CashAccountBalanceOut]:
        self._require_access(user)
        rows = self.repo.approved_rows_for_balance(filters)
        accounts = self.repo.cash_accounts(filters)
        out: list[CashAccountBalanceOut] = []
        for account in sorted(accounts, key=lambda item: str(item.get("name") or "")):
            account_id = account["id"]
            opening_balance = float(account.get("opening_balance") or 0)
            opening_date = str(account["opening_balance_date"])
            inflow = 0.0
            outflow = 0.0
            for row in rows:
                if row["cash_account_id"] != account_id:
                    continue
                if str(row["transaction_date"]) < opening_date:
                    continue
                if row["direction"] == "INFLOW":
                    inflow += _amount(row)
                else:
                    outflow += _amount(row)
            out.append(
                CashAccountBalanceOut(
                    cash_account_id=account_id,
                    cash_account_name=account["name"],
                    currency=account.get("currency") or "IDR",
                    opening_balance=opening_balance,
                    inflow=inflow,
                    outflow=outflow,
                    current_balance=opening_balance + inflow - outflow,
                )
            )
        return out

    def pending_approvals(
        self, filters: ReportFilters, user: CurrentUser
    ) -> PendingApprovalsOut:
        self._require_access(user)
        return PendingApprovalsOut(count=self.repo.pending_approvals_count(filters))

    def export(self, data: ExportRequest, user: CurrentUser) -> tuple[bytes, str, str]:
        self._require_access(user)
        title, rows = self._export_rows(data)
        if data.format == ExportFormat.XLSX:
            return (
                self._xlsx(title, rows),
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                f"{data.report_type.value}.xlsx",
            )
        return self._pdf(title, rows), "application/pdf", f"{data.report_type.value}.pdf"

    def _summary_from_rows(self, rows: Rows) -> SummaryOut:
        total_inflow = sum(_amount(row) for row in rows if row["direction"] == "INFLOW")
        total_outflow = sum(_amount(row) for row in rows if row["direction"] == "OUTFLOW")
        return SummaryOut(
            totalInflow=total_inflow,
            totalOutflow=total_outflow,
            netCashflow=total_inflow - total_outflow,
            currency="IDR",
        )

    def _export_rows(self, data: ExportRequest) -> tuple[str, list[list[object]]]:
        filters = data.filters()
        match data.report_type:
            case ReportType.SUMMARY:
                summary = self._summary_from_rows(self.repo.approved_rows(filters))
                return "Summary", [
                    ["Metric", "Value"],
                    ["Total inflow", summary.totalInflow],
                    ["Total outflow", summary.totalOutflow],
                    ["Net cashflow", summary.netCashflow],
                    ["Currency", summary.currency],
                ]
            case ReportType.MONTHLY_TREND:
                monthly_values = self.monthly_trend(filters, _report_user())
                return "Monthly trend", _rows_from_models(
                    ["Month", "Inflow", "Outflow", "Net"],
                    ([v.month, v.inflow, v.outflow, v.net] for v in monthly_values),
                )
            case ReportType.BY_CATEGORY:
                category_values = self.by_category(filters, _report_user())
                return "By category", _rows_from_models(
                    ["Category", "Direction", "Amount"],
                    ([v.category_name, v.direction, v.amount] for v in category_values),
                )
            case ReportType.BY_DEPARTMENT:
                department_values = self.by_department(filters, _report_user())
                return "By department", _rows_from_models(
                    ["Department", "Inflow", "Outflow", "Net"],
                    (
                        [v.department_name, v.inflow, v.outflow, v.net]
                        for v in department_values
                    ),
                )
            case ReportType.CASH_ACCOUNT_BALANCES:
                balance_values = self.cash_account_balances(filters, _report_user())
                return "Cash account balances", _rows_from_models(
                    ["Cash account", "Opening", "Inflow", "Outflow", "Balance"],
                    (
                        [
                            v.cash_account_name,
                            v.opening_balance,
                            v.inflow,
                            v.outflow,
                            v.current_balance,
                        ]
                        for v in balance_values
                    ),
                )

    def _xlsx(self, title: str, rows: list[list[object]]) -> bytes:
        wb = Workbook()
        ws = wb.active
        ws.title = title[:31]
        for row in rows:
            ws.append(row)
        buffer = BytesIO()
        wb.save(buffer)
        return buffer.getvalue()

    def _pdf(self, title: str, rows: list[list[object]]) -> bytes:
        buffer = BytesIO()
        document = SimpleDocTemplate(buffer, pagesize=A4)
        table = Table([[str(cell) for cell in row] for row in rows])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ]
            )
        )
        _ = title
        document.build([table])
        return buffer.getvalue()


def _rows_from_models(
    header: list[object], rows: Iterable[list[object]]
) -> list[list[object]]:
    return [header, *rows]


def _report_user() -> CurrentUser:
    return CurrentUser(
        id="report-export",
        role=Role.FINANCE_ADMIN,
        full_name="Report Export",
        status=UserStatus.ACTIVE,
    )
