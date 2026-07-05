import type { Metadata } from "next";
import type { ReactNode } from "react";
import { Inter } from "next/font/google";

import { AppShell } from "@/components/layout/AppShell";
import { apiGet } from "@/lib/api";
import type { AppNotification, CurrentUser, UnreadCount } from "@/lib/types";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

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

async function getNotificationData(
  user: CurrentUser | null
): Promise<{ notifications: AppNotification[]; unreadCount: number }> {
  if (!user) {
    return { notifications: [], unreadCount: 0 };
  }
  try {
    const [notifications, unread] = await Promise.all([
      apiGet<AppNotification[]>("/api/notifications?limit=5"),
      apiGet<UnreadCount>("/api/notifications/unread-count"),
    ]);
    return { notifications, unreadCount: unread.count };
  } catch {
    return { notifications: [], unreadCount: 0 };
  }
}

export default async function RootLayout({ children }: { children: ReactNode }) {
  const user = await getCurrentUser();
  const { notifications, unreadCount } = await getNotificationData(user);
  return (
    <html lang="en" className={inter.variable}>
      <body>
        <AppShell
          user={user}
          notifications={notifications}
          unreadCount={unreadCount}
        >
          {children}
        </AppShell>
      </body>
    </html>
  );
}