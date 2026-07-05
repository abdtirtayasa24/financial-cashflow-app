from typing import Any, cast

from supabase import Client

from app.modules.reports.schemas import ReportFilters

Rows = list[dict[str, Any]]


class ReportRepository:
    approved_view = "approved_cashflow_report_base"

    def __init__(self, db: Client) -> None:
        self.db = db

    def approved_rows(self, filters: ReportFilters) -> Rows:
        query = self.db.table(self.approved_view).select("*")
        if filters.date_from:
            query = query.gte("transaction_date", filters.date_from)
        if filters.date_to:
            query = query.lte("transaction_date", filters.date_to)
        if filters.department_id:
            query = query.eq("department_id", filters.department_id)
        if filters.category_id:
            query = query.eq("category_id", filters.category_id)
        if filters.cash_account_id:
            query = query.eq("cash_account_id", filters.cash_account_id)
        return cast(Rows, query.execute().data)

    def approved_rows_for_balance(self, filters: ReportFilters) -> Rows:
        query = self.db.table(self.approved_view).select("*")
        if filters.department_id:
            query = query.eq("department_id", filters.department_id)
        if filters.category_id:
            query = query.eq("category_id", filters.category_id)
        if filters.cash_account_id:
            query = query.eq("cash_account_id", filters.cash_account_id)
        return cast(Rows, query.execute().data)

    def cash_accounts(self, filters: ReportFilters) -> Rows:
        query = self.db.table("cash_accounts").select("*")
        if filters.cash_account_id:
            query = query.eq("id", filters.cash_account_id)
        return cast(Rows, query.execute().data)

    def pending_approvals_count(self, filters: ReportFilters) -> int:
        query = (
            self.db.table("cashflow_transactions")
            .select("id")
            .eq("status", "SUBMITTED")
        )
        if filters.date_from:
            query = query.gte("transaction_date", filters.date_from)
        if filters.date_to:
            query = query.lte("transaction_date", filters.date_to)
        if filters.department_id:
            query = query.eq("department_id", filters.department_id)
        return len(cast(Rows, query.execute().data))
