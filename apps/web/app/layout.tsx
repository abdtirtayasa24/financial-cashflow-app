import type { Metadata } from "next";
import type { ReactNode } from "react";

import { AppShell } from "@/components/layout/AppShell";
import { apiGet } from "@/lib/api";
import type { CurrentUser } from "@/lib/types";
import "./globals.css";

export const metadata: Metadata = {
  title: "Financial Cashflow",
  description: "Cashflow recording and BI reporting application",
};

async function getCurrentUser(): Promise<CurrentUser | null> {
  try {
    return await apiGet<CurrentUser>("/api/me");
  } catch {
    return null;
  }
}

export default async function RootLayout({ children }: { children: ReactNode }) {
  const user = await getCurrentUser();
  return (
    <html lang="en">
      <body>
        <AppShell user={user}>{children}</AppShell>
      </body>
    </html>
  );
}