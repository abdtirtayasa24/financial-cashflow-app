import { DashboardClient } from "@/components/dashboard/DashboardClient";
import { apiGet, isApiError } from "@/lib/api";
import type {
  CashAccount,
  CashAccountBalancePoint,
  CategoryBreakdownPoint,
  CurrentUser,
  Department,
  DepartmentBreakdownPoint,
  MonthlyTrendPoint,
  PendingApprovalsCount,
  ReportSummary,
} from "@/lib/types";

interface DashboardFilters {
  date_from: string;
  date_to: string;
  department_id: string;
  cash_account_id: string;
}

interface DashboardData {
  departments: Department[];
  cashAccounts: CashAccount[];
  summary: ReportSummary;
  monthlyTrend: MonthlyTrendPoint[];
  byCategory: CategoryBreakdownPoint[];
  byDepartment: DepartmentBreakdownPoint[];
  cashAccountBalances: CashAccountBalancePoint[];
  pendingApprovals: PendingApprovalsCount;
}

function filtersFromSearchParams(
  params: Record<string, string | undefined>
): DashboardFilters {
  return {
    date_from: params.date_from ?? "",
    date_to: params.date_to ?? "",
    department_id: params.department_id ?? "",
    cash_account_id: params.cash_account_id ?? "",
  };
}

function reportPath(path: string, filters: DashboardFilters): string {
  const sp = new URLSearchParams();
  if (filters.date_from) sp.set("date_from", filters.date_from);
  if (filters.date_to) sp.set("date_to", filters.date_to);
  if (filters.department_id) sp.set("department_id", filters.department_id);
  if (filters.cash_account_id) sp.set("cash_account_id", filters.cash_account_id);
  const query = sp.toString();
  return query ? `${path}?${query}` : path;
}

async function loadDashboardData(filters: DashboardFilters): Promise<DashboardData> {
  const [
    departments,
    cashAccounts,
    summary,
    monthlyTrend,
    byCategory,
    byDepartment,
    cashAccountBalances,
    pendingApprovals,
  ] = await Promise.all([
    apiGet<Department[]>("/api/departments"),
    apiGet<CashAccount[]>("/api/cash-accounts"),
    apiGet<ReportSummary>(reportPath("/api/reports/summary", filters)),
    apiGet<MonthlyTrendPoint[]>(reportPath("/api/reports/monthly-trend", filters)),
    apiGet<CategoryBreakdownPoint[]>(reportPath("/api/reports/by-category", filters)),
    apiGet<DepartmentBreakdownPoint[]>(reportPath("/api/reports/by-department", filters)),
    apiGet<CashAccountBalancePoint[]>(
      reportPath("/api/reports/cash-account-balances", filters)
    ),
    apiGet<PendingApprovalsCount>(
      reportPath("/api/reports/pending-approvals", filters)
    ),
  ]);

  return {
    departments,
    cashAccounts,
    summary,
    monthlyTrend,
    byCategory,
    byDepartment,
    cashAccountBalances,
    pendingApprovals,
  };
}

export default async function DashboardPage({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | undefined>>;
}) {
  const params = await searchParams;
  const filters = filtersFromSearchParams(params);
  const user = await apiGet<CurrentUser>("/api/me");
  let data: DashboardData | null = null;

  try {
    data = await loadDashboardData(filters);
  } catch (error) {
    if (!isApiError(error) || error.status !== 403) {
      throw error;
    }
    data = null;
  }

  if (!data) {
    return (
      <div className="container">
        <div className="empty">
          <div className="empty__title">Dashboard is restricted</div>
          <p className="empty__desc">
            Financial dashboard access is available to Finance Admin and Management users.
          </p>
        </div>
      </div>
    );
  }

  return (
    <DashboardClient
      key={reportPath("/dashboard", filters)}
      userName={user.full_name}
      initialFilters={filters}
      departments={data.departments}
      cashAccounts={data.cashAccounts}
      summary={data.summary}
      monthlyTrend={data.monthlyTrend}
      byCategory={data.byCategory}
      byDepartment={data.byDepartment}
      cashAccountBalances={data.cashAccountBalances}
      pendingApprovals={data.pendingApprovals}
    />
  );
}
