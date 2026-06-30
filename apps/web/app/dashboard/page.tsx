import { apiGet } from "@/lib/api";
import type { CurrentUser } from "@/lib/types";

export default async function DashboardPage() {
  const user = await apiGet<CurrentUser>("/api/me");
  return (
    <div className="container">
      <h1>Dashboard</h1>
      <p className="muted">
        Welcome, {user.full_name}. The BI dashboard (KPIs, charts, filters)
        is delivered in Milestone #7. Transaction entry and approvals arrive in
        Milestones #3 and #4.
      </p>
    </div>
  );
}