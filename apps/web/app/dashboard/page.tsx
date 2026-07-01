import { apiGet } from "@/lib/api";
import type { CurrentUser } from "@/lib/types";

export default async function DashboardPage() {
  const user = await apiGet<CurrentUser>("/api/me");
  return (
    <div className="container">
      <div className="page-header">
        <div>
          <h1>Dashboard</h1>
          <p className="page-header__subtitle">
            Welcome back, {user.full_name}. Cashflow overview and analytics will appear here.
          </p>
        </div>
      </div>
      <div className="empty">
        <div className="empty__icon" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M3 3v18h18" />
            <path d="M7 14l4-4 4 4 5-5" />
          </svg>
        </div>
        <div className="empty__title">Dashboard coming soon</div>
        <p className="empty__desc">
          The BI dashboard with KPIs, charts, and filters will be available once transaction data is flowing.
        </p>
      </div>
    </div>
  );
}