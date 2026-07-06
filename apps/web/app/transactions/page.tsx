import Link from "next/link";

import { apiGet } from "@/lib/api";
import { getCurrentUser } from "@/lib/current-user";
import { formatDate, formatIDR } from "@/lib/format";
import type {
  CashAccount,
  Category,
  Department,
  Transaction,
} from "@/lib/types";
import { DIRECTIONS, TRANSACTION_STATUSES, isFinanceRole } from "@/lib/types";
import { StatusBadge } from "@/components/StatusBadge";

const PAGE_SIZE = 50;

function statusLabel(s: string): string {
  return s.charAt(0) + s.slice(1).toLowerCase();
}

function buildApiPath(filters: Record<string, string | undefined>, offset: number): string {
  const sp = new URLSearchParams();
  for (const [k, v] of Object.entries(filters)) {
    if (k === "page" || !v) continue;
    sp.set(k, v);
  }
  sp.set("limit", String(PAGE_SIZE));
  sp.set("offset", String(offset));
  return `/api/transactions?${sp.toString()}`;
}

function pageHref(filters: Record<string, string | undefined>, page: number): string {
  const sp = new URLSearchParams();
  for (const [k, v] of Object.entries(filters)) {
    if (k === "page" || !v) continue;
    sp.set(k, v);
  }
  if (page > 1) sp.set("page", String(page));
  const qs = sp.toString();
  return qs ? `/transactions?${qs}` : "/transactions";
}

export default async function TransactionsPage({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | undefined>>;
}) {
  const filters = await searchParams;
  const user = await getCurrentUser();
  const page = Math.max(1, parseInt(filters.page ?? "1", 10) || 1);
  const offset = (page - 1) * PAGE_SIZE;

  const [transactions, departments, categories, cashAccounts] = await Promise.all([
    apiGet<Transaction[]>(buildApiPath(filters, offset)),
    apiGet<Department[]>("/api/departments"),
    apiGet<Category[]>("/api/categories"),
    apiGet<CashAccount[]>("/api/cash-accounts"),
  ]);

  const deptName = (id: string) =>
    departments.find((d) => d.id === id)?.name ?? "—";
  const canCreate =
    user?.role === "EMPLOYEE" || isFinanceRole(user?.role);
  const hasMore = transactions.length === PAGE_SIZE;

  return (
    <div className="container">
      <div className="page-header">
        <div>
          <h1>Transactions</h1>
          <p className="page-header__subtitle">
            Record and track cash inflows and outflows.
          </p>
        </div>
        {canCreate ? (
          <Link href="/transactions/new" className="btn-primary">
            New transaction
          </Link>
        ) : null}
      </div>

      <div className="section">
        <form method="get" className="card filters" aria-label="Filter transactions">
          <div className="filters__row">
            <div className="field">
              <label htmlFor="date_from">From</label>
              <input id="date_from" name="date_from" type="date" defaultValue={filters.date_from} />
            </div>
            <div className="field">
              <label htmlFor="date_to">To</label>
              <input id="date_to" name="date_to" type="date" defaultValue={filters.date_to} />
            </div>
            <div className="field">
              <label htmlFor="department_id">Department</label>
              <select id="department_id" name="department_id" defaultValue={filters.department_id ?? ""}>
                <option value="">All</option>
                {departments.map((d) => (
                  <option key={d.id} value={d.id}>{d.name}</option>
                ))}
              </select>
            </div>
            <div className="field">
              <label htmlFor="category_id">Category</label>
              <select id="category_id" name="category_id" defaultValue={filters.category_id ?? ""}>
                <option value="">All</option>
                {categories.map((c) => (
                  <option key={c.id} value={c.id}>{c.name}</option>
                ))}
              </select>
            </div>
          </div>
          <div className="filters__row">
            <div className="field">
              <label htmlFor="cash_account_id">Cash account</label>
              <select id="cash_account_id" name="cash_account_id" defaultValue={filters.cash_account_id ?? ""}>
                <option value="">All</option>
                {cashAccounts.map((c) => (
                  <option key={c.id} value={c.id}>{c.name}</option>
                ))}
              </select>
            </div>
            <div className="field">
              <label htmlFor="status">Status</label>
              <select id="status" name="status" defaultValue={filters.status ?? ""}>
                <option value="">All</option>
                {TRANSACTION_STATUSES.map((s) => (
                  <option key={s} value={s}>{statusLabel(s)}</option>
                ))}
              </select>
            </div>
            <div className="field">
              <label htmlFor="direction">Direction</label>
              <select id="direction" name="direction" defaultValue={filters.direction ?? ""}>
                <option value="">All</option>
                {DIRECTIONS.map((d) => (
                  <option key={d} value={d}>{d === "INFLOW" ? "Inflow" : "Outflow"}</option>
                ))}
              </select>
            </div>
            <div className="filters__actions">
              <button type="submit" className="btn-primary">Apply filters</button>
              <Link href="/transactions" className="btn-ghost">Clear</Link>
            </div>
          </div>
        </form>
      </div>

      <div className="section">
        <h2 className="section__title">All transactions</h2>
        {transactions.length === 0 ? (
          <div className="empty">
            <div className="empty__icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M17 1l4 4-4 4" />
                <path d="M3 11V9a4 4 0 0 1 4-4h14" />
                <path d="M7 23l-4-4 4-4" />
                <path d="M21 13v2a4 4 0 0 1-4 4H3" />
              </svg>
            </div>
            <div className="empty__title">No transactions found</div>
            <p className="empty__desc">
              {canCreate
                ? "Create your first transaction to start recording cashflow."
                : "Transactions will appear here once they are created."}
            </p>
          </div>
        ) : (
          <div className="table-wrap">
            <table className="table">
              <thead>
                <tr>
                  <th>Transaction no.</th>
                  <th>Date</th>
                  <th>Direction</th>
                  <th>Amount</th>
                  <th>Department</th>
                  <th>Status</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {transactions.map((t) => (
                  <tr key={t.id}>
                    <td className="tnum text-secondary">{t.transaction_no}</td>
                    <td>{formatDate(t.transaction_date)}</td>
                    <td>{t.direction === "INFLOW" ? "Inflow" : "Outflow"}</td>
                    <td className="tnum" style={{ fontWeight: 500 }}>
                      {formatIDR(t.amount)}
                    </td>
                    <td className="text-secondary">{deptName(t.department_id)}</td>
                    <td><StatusBadge status={t.status} /></td>
                    <td>
                      <Link href={`/transactions/${t.id}`} className="btn-ghost btn-sm">
                        View
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <div className="pagination" role="navigation" aria-label="Pagination">
        {page > 1 ? (
          <Link href={pageHref(filters, page - 1)} className="btn-ghost btn-sm">
            Previous
          </Link>
        ) : (
          <span className="btn-ghost btn-sm" aria-disabled="true">Previous</span>
        )}
        <span className="pagination__page tnum">Page {page}</span>
        {hasMore ? (
          <Link href={pageHref(filters, page + 1)} className="btn-ghost btn-sm">
            Next
          </Link>
        ) : (
          <span className="btn-ghost btn-sm" aria-disabled="true">Next</span>
        )}
      </div>
    </div>
  );
}