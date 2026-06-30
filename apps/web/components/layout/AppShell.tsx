import type { ReactNode } from "react";

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div>
      <header
        style={{
          display: "flex",
          alignItems: "center",
          gap: 12,
          padding: "12px 16px",
          borderBottom: "1px solid #e2e8f0",
        }}
      >
        <strong>Financial Cashflow</strong>
      </header>
      <section style={{ padding: 16 }}>{children}</section>
    </div>
  );
}