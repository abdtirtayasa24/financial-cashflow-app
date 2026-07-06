import Link from "next/link";

import { ApproveForm, RejectForm } from "@/components/ReviewActions";
import { StatusBadge } from "@/components/StatusBadge";
import { apiGet } from "@/lib/api";
import { getCurrentUser } from "@/lib/current-user";
import { formatDate, formatIDR } from "@/lib/format";
import type { Department, Transaction } from "@/lib/types";
import { isFinanceRole } from "@/lib/types";

const PAGE_SIZE = 50;

function buildApiPath(offset: number): string {
  const sp = new URLSearchParams();
  sp.set("status", "SUBMITTED");
  sp.set("limit", String(PAGE_SIZE));
  sp.set("offset", String(offset));
  return `/api/transactions?${sp.toString()}`;
}

function pageHref(page: number): string {
  return page > 1 ? `/approvals?page=${page}` : "/approvals";
}

export default async function ApprovalsPage({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | undefined>>;
}) {
  const user = await getCurrentUser();
  const params = await searchParams;
  const page = Math.max(1, parseInt(params.page ?? "1", 10) || 1);
  const offset = (page - 1) * PAGE_SIZE;

  if (!user || !isFinanceRole(user.role)) {
    return (
      <div className="container">
        <div className="empty">
          <div className="empty__title">Approvals are restricted</div>
          <p className="empty__desc">
            Only Finance Admin or Management users can approve, reject, or void transactions.
          </p>
        </div>
      </div>
    );
  }

  const [transactions, departments] = await Promise.all([
    apiGet<Transaction[]>(buildApiPath(offset)),
    apiGet<Department[]>("/api/departments"),
  ]);
  const hasMore = transactions.length === PAGE_SIZE;
  const deptName = (id: string) => departments.find((d) => d.id === id)?.name ?? "—";

  return (
    <div className="container">
      <div className="page-header">
        <div>
          <h1>Approvals</h1>
          <p className="page-header__subtitle">
            Review submitted cashflow transactions before they become official.
          </p>
        </div>
      </div>

      <div className="section">
        <h2 className="section__title">Submitted transactions</h2>
        {transactions.length === 0 ? (
          <div className="empty">
            <div className="empty__title">No pending approvals</div>
            <p className="empty__desc">
              Submitted transactions will appear here for Finance Admin review.
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
                  <th>Creator</th>
                  <th>Status</th>
                  <th>Actions</th>
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
                    <td className="text-tertiary text-sm tnum">{t.created_by}</td>
                    <td><StatusBadge status={t.status} /></td>
                    <td>
                      <div className="approval-actions">
                        <Link href={`/transactions/${t.id}`} className="btn-ghost btn-sm">
                          View
                        </Link>
                        <ApproveForm id={t.id} />
                        <RejectForm id={t.id} />
                      </div>
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
          <Link href={pageHref(page - 1)} className="btn-ghost btn-sm">
            Previous
          </Link>
        ) : (
          <span className="btn-ghost btn-sm" aria-disabled="true">Previous</span>
        )}
        <span className="pagination__page tnum">Page {page}</span>
        {hasMore ? (
          <Link href={pageHref(page + 1)} className="btn-ghost btn-sm">
            Next
          </Link>
        ) : (
          <span className="btn-ghost btn-sm" aria-disabled="true">Next</span>
        )}
      </div>
    </div>
  );
}
