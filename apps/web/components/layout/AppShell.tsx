import type { ReactNode } from "react";

import { signOut } from "@/app/actions";
import type { CurrentUser } from "@/lib/types";

interface AppShellProps {
  user: CurrentUser | null;
  children: ReactNode;
}

export function AppShell({ user, children }: AppShellProps) {
  const isAdmin = user?.role === "SYSTEM_ADMIN";

  return (
    <div className="shell">
      <header className="shell__header">
        <div className="shell__brand">Financial Cashflow</div>
        <nav className="shell__nav" aria-label="Main">
          {user ? <a href="/dashboard">Dashboard</a> : null}
          {isAdmin ? (
            <>
              <a href="/admin/users">Users</a>
              <a href="/admin/departments">Departments</a>
              <a href="/admin/categories">Categories</a>
              <a href="/admin/payment-methods">Payment Methods</a>
              <a href="/admin/cash-accounts">Cash Accounts</a>
              <a href="/admin/settings">Settings</a>
            </>
          ) : null}
          {user ? (
            <form action={signOut}>
              <button type="submit" className="btn-ghost btn-sm">
                Sign out
              </button>
            </form>
          ) : null}
        </nav>
      </header>
      <main className="shell__main">{children}</main>
      {user ? (
        <div className="shell__user container">
          Signed in as {user.full_name} ({user.role})
        </div>
      ) : null}
    </div>
  );
}