from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class ExportFormat(StrEnum):
    XLSX = "xlsx"
    PDF = "pdf"


class ReportType(StrEnum):
    SUMMARY = "summary"
    MONTHLY_TREND = "monthly-trend"
    BY_CATEGORY = "by-category"
    BY_DEPARTMENT = "by-department"
    CASH_ACCOUNT_BALANCES = "cash-account-balances"


class ReportFilters(BaseModel):
    date_from: str | None = None
    date_to: str | None = None
    department_id: str | None = None
    category_id: str | None = None
    cash_account_id: str | None = None


class SummaryOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    totalInflow: float
    totalOutflow: float
    netCashflow: float
    currency: str = "IDR"


class MonthlyTrendOut(BaseModel):
    month: str
    inflow: float
    outflow: float
    net: float


class CategoryBreakdownOut(BaseModel):
    category_id: str
    category_name: str
    direction: str
    amount: float


class DepartmentBreakdownOut(BaseModel):
    department_id: str
    department_name: str
    inflow: float
    outflow: float
    net: float


class CashAccountBalanceOut(BaseModel):
    cash_account_id: str
    cash_account_name: str
    currency: str
    opening_balance: float
    inflow: float
    outflow: float
    current_balance: float


class PendingApprovalsOut(BaseModel):
    count: int = Field(ge=0)


class ExportRequest(BaseModel):
    format: ExportFormat
    report_type: ReportType
    date_from: str | None = None
    date_to: str | None = None
    department_id: str | None = None
    category_id: str | None = None
    cash_account_id: str | None = None

    def filters(self) -> ReportFilters:
        return ReportFilters(
            date_from=self.date_from,
            date_to=self.date_to,
            department_id=self.department_id,
            category_id=self.category_id,
            cash_account_id=self.cash_account_id,
        )
