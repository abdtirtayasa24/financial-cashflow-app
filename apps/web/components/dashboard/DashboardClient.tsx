"use client";

import { useMemo, useState, useTransition, type ReactNode } from "react";
import { useRouter } from "next/navigation";
import type { EChartsOption } from "echarts";
import { AlertTriangle, ArrowDownCircle, ArrowUpCircle, Clock3, Landmark } from "lucide-react";

import { EChart } from "@/components/dashboard/EChart";
import { formatIDR } from "@/lib/format";
import type {
  CashAccount,
  CashAccountBalancePoint,
  CategoryBreakdownPoint,
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

interface DashboardClientProps {
  userName: string;
  initialFilters: DashboardFilters;
  departments: Department[];
  cashAccounts: CashAccount[];
  summary: ReportSummary;
  monthlyTrend: MonthlyTrendPoint[];
  byCategory: CategoryBreakdownPoint[];
  byDepartment: DepartmentBreakdownPoint[];
  cashAccountBalances: CashAccountBalancePoint[];
  pendingApprovals: PendingApprovalsCount;
}

function buildHref(filters: DashboardFilters): string {
  const sp = new URLSearchParams();
  for (const [key, value] of Object.entries(filters)) {
    if (value) sp.set(key, value);
  }
  const query = sp.toString();
  return query ? `/dashboard?${query}` : "/dashboard";
}

function KpiCard({
  label,
  value,
  hint,
  tone,
  icon,
}: {
  label: string;
  value: string;
  hint: string;
  tone: "inflow" | "outflow" | "net" | "balance";
  icon: ReactNode;
}) {
  return (
    <div className={`dashboard-kpi dashboard-kpi--${tone}`}>
      <div className="dashboard-kpi__icon" aria-hidden="true">
        {icon}
      </div>
      <div>
        <div className="dashboard-kpi__label">{label}</div>
        <div className="dashboard-kpi__value">{value}</div>
        <div className="dashboard-kpi__hint">{hint}</div>
      </div>
    </div>
  );
}

function ChartCard({
  title,
  description,
  empty,
  children,
}: {
  title: string;
  description: string;
  empty?: boolean;
  children: ReactNode;
}) {
  return (
    <div className="dashboard-chart-card">
      <div className="dashboard-chart-card__header">
        <h2>{title}</h2>
        <p>{description}</p>
      </div>
      {empty ? (
        <div className="dashboard-chart-empty">No data for the selected filters.</div>
      ) : (
        children
      )}
    </div>
  );
}

export function DashboardClient({
  userName,
  initialFilters,
  departments,
  cashAccounts,
  summary,
  monthlyTrend,
  byCategory,
  byDepartment,
  cashAccountBalances,
  pendingApprovals,
}: DashboardClientProps) {
  const router = useRouter();
  const [pending, startTransition] = useTransition();
  const [filters, setFilters] = useState(initialFilters);

  const currentCashBalance = cashAccountBalances.reduce(
    (sum, item) => sum + item.current_balance,
    0
  );
  const outflowCategories = byCategory.filter((item) => item.direction === "OUTFLOW");

  const trendOption = useMemo<EChartsOption>(() => ({
    color: ["#059669", "#dc2626"],
    tooltip: { trigger: "axis" },
    legend: { top: 0 },
    grid: { left: 48, right: 24, top: 48, bottom: 36 },
    xAxis: { type: "category", data: monthlyTrend.map((item) => item.month) },
    yAxis: { type: "value" },
    series: [
      { name: "Inflow", type: "bar", data: monthlyTrend.map((item) => item.inflow) },
      { name: "Outflow", type: "bar", data: monthlyTrend.map((item) => item.outflow) },
      { name: "Net", type: "line", data: monthlyTrend.map((item) => item.net), smooth: true },
    ],
  }), [monthlyTrend]);

  const categoryOption = useMemo<EChartsOption>(() => ({
    color: ["#dc2626", "#f97316", "#f59e0b", "#7c3aed", "#0f766e"],
    tooltip: { trigger: "item" },
    legend: { bottom: 0, type: "scroll" },
    series: [
      {
        name: "Expense",
        type: "pie",
        radius: ["44%", "70%"],
        center: ["50%", "46%"],
        data: outflowCategories.map((item) => ({ name: item.category_name, value: item.amount })),
      },
    ],
  }), [outflowCategories]);

  const departmentOption = useMemo<EChartsOption>(() => ({
    color: ["#2563eb", "#64748b"],
    tooltip: { trigger: "axis" },
    legend: { top: 0 },
    grid: { left: 48, right: 24, top: 48, bottom: 48 },
    xAxis: {
      type: "category",
      axisLabel: { rotate: 25 },
      data: byDepartment.map((item) => item.department_name),
    },
    yAxis: { type: "value" },
    series: [
      { name: "Inflow", type: "bar", data: byDepartment.map((item) => item.inflow) },
      { name: "Outflow", type: "bar", data: byDepartment.map((item) => item.outflow) },
      { name: "Net", type: "line", data: byDepartment.map((item) => item.net), smooth: true },
    ],
  }), [byDepartment]);

  const balanceOption = useMemo<EChartsOption>(() => ({
    color: ["#0f766e"],
    tooltip: { trigger: "axis" },
    grid: { left: 48, right: 24, top: 24, bottom: 56 },
    xAxis: {
      type: "category",
      axisLabel: { rotate: 25 },
      data: cashAccountBalances.map((item) => item.cash_account_name),
    },
    yAxis: { type: "value" },
    series: [
      {
        name: "Current balance",
        type: "bar",
        data: cashAccountBalances.map((item) => item.current_balance),
      },
    ],
  }), [cashAccountBalances]);

  function updateFilter(key: keyof DashboardFilters, value: string) {
    const next = { ...filters, [key]: value };
    setFilters(next);
    startTransition(() => router.replace(buildHref(next), { scroll: false }));
  }

  function resetFilters() {
    const next = { date_from: "", date_to: "", department_id: "", cash_account_id: "" };
    setFilters(next);
    startTransition(() => router.replace("/dashboard", { scroll: false }));
  }

  return (
    <div className="container dashboard-page">
      <div className="page-header dashboard-hero">
        <div>
          <h1>Dashboard</h1>
          <p className="page-header__subtitle">
            Welcome back, {userName}. Monitor approved cashflow performance and liquidity.
          </p>
        </div>
        <div className="dashboard-pending">
          <Clock3 size={18} />
          <span className="dashboard-pending__count">{pendingApprovals.count}</span>
          <span>pending approvals</span>
        </div>
      </div>

      <div className="section">
        <div className="card dashboard-filters" aria-label="Dashboard filters">
          <div className="field">
            <label htmlFor="date_from">From</label>
            <input
              id="date_from"
              type="date"
              value={filters.date_from}
              onChange={(event) => updateFilter("date_from", event.target.value)}
            />
          </div>
          <div className="field">
            <label htmlFor="date_to">To</label>
            <input
              id="date_to"
              type="date"
              value={filters.date_to}
              onChange={(event) => updateFilter("date_to", event.target.value)}
            />
          </div>
          <div className="field">
            <label htmlFor="department_id">Department</label>
            <select
              id="department_id"
              value={filters.department_id}
              onChange={(event) => updateFilter("department_id", event.target.value)}
            >
              <option value="">All departments</option>
              {departments.map((department) => (
                <option key={department.id} value={department.id}>{department.name}</option>
              ))}
            </select>
          </div>
          <div className="field">
            <label htmlFor="cash_account_id">Cash account</label>
            <select
              id="cash_account_id"
              value={filters.cash_account_id}
              onChange={(event) => updateFilter("cash_account_id", event.target.value)}
            >
              <option value="">All cash accounts</option>
              {cashAccounts.map((account) => (
                <option key={account.id} value={account.id}>{account.name}</option>
              ))}
            </select>
          </div>
          <button type="button" className="btn-ghost" onClick={resetFilters} disabled={pending}>
            Reset
          </button>
        </div>
      </div>

      <div className="dashboard-kpi-grid" aria-live="polite">
        <KpiCard
          label="Total inflow"
          value={formatIDR(summary.totalInflow)}
          hint="Scoped to selected period"
          tone="inflow"
          icon={<ArrowUpCircle size={20} />}
        />
        <KpiCard
          label="Total outflow"
          value={formatIDR(summary.totalOutflow)}
          hint="Scoped to selected period"
          tone="outflow"
          icon={<ArrowDownCircle size={20} />}
        />
        <KpiCard
          label="Net cashflow"
          value={formatIDR(summary.netCashflow)}
          hint="Inflow minus outflow"
          tone="net"
          icon={<AlertTriangle size={20} />}
        />
        <KpiCard
          label="Current cash balance"
          value={formatIDR(currentCashBalance)}
          hint="As of now, not date-range filtered"
          tone="balance"
          icon={<Landmark size={20} />}
        />
      </div>

      <div className="dashboard-grid section">
        <ChartCard
          title="Monthly cashflow trend"
          description="Approved inflow, outflow, and net movement by month."
          empty={monthlyTrend.length === 0}
        >
          <EChart option={trendOption} ariaLabel="Monthly cashflow trend chart" />
        </ChartCard>
        <ChartCard
          title="Expense by category"
          description="Approved outflow grouped by exact category."
          empty={outflowCategories.length === 0}
        >
          <EChart option={categoryOption} ariaLabel="Expense by category chart" />
        </ChartCard>
        <ChartCard
          title="Cashflow by department"
          description="Approved inflow, outflow, and net by exact department."
          empty={byDepartment.length === 0}
        >
          <EChart option={departmentOption} ariaLabel="Cashflow by department chart" />
        </ChartCard>
        <ChartCard
          title="Cash account balances"
          description="Current balance by account, calculated as-of now."
          empty={cashAccountBalances.length === 0}
        >
          <EChart option={balanceOption} ariaLabel="Cash account balances chart" />
        </ChartCard>
      </div>
    </div>
  );
}
