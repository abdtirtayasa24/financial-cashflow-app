"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState, type ReactNode } from "react";
import {
  Bell,
  Building2,
  ClipboardCheck,
  CreditCard,
  LayoutDashboard,
  LogOut,
  Menu,
  ReceiptText,
  Repeat,
  Settings,
  Tags,
  Upload,
  Users,
  Wallet,
} from "lucide-react";

import {
  markAllNotificationsRead,
  markNotificationRead,
  signOut,
} from "@/app/actions";
import { formatDateTime } from "@/lib/format";
import type { AppNotification, CurrentUser } from "@/lib/types";

interface AppShellProps {
  user: CurrentUser | null;
  notifications: AppNotification[];
  unreadCount: number;
  children: ReactNode;
}

interface NavItem {
  href: string;
  label: string;
  icon: typeof LayoutDashboard;
  roles?: CurrentUser["role"][];
}

const mainNav: NavItem[] = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/transactions", label: "Transactions", icon: ReceiptText },
  {
    href: "/recurring",
    label: "Recurring",
    icon: Repeat,
    roles: ["FINANCE_ADMIN", "EMPLOYEE", "DEPARTMENT_MANAGER"],
  },
];

const financeNav: NavItem[] = [
  { href: "/approvals", label: "Approvals", icon: ClipboardCheck },
  { href: "/import", label: "Import", icon: Upload },
];

const adminNav: NavItem[] = [
  { href: "/admin/users", label: "Users", icon: Users },
  { href: "/admin/departments", label: "Departments", icon: Building2 },
  { href: "/admin/categories", label: "Categories", icon: Tags },
  { href: "/admin/payment-methods", label: "Payment Methods", icon: CreditCard },
  { href: "/admin/cash-accounts", label: "Cash Accounts", icon: Wallet },
  { href: "/admin/settings", label: "Settings", icon: Settings },
];

function isActive(pathname: string, href: string): boolean {
  if (href === "/dashboard") return pathname === "/dashboard";
  return pathname === href || pathname.startsWith(href + "/");
}

function getInitials(name: string): string {
  const parts = name.trim().split(/\s+/);
  if (parts.length >= 2) {
    return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
  }
  return name.slice(0, 2).toUpperCase();
}

function formatRole(role: string): string {
  return role
    .split("_")
    .map((w) => w.charAt(0) + w.slice(1).toLowerCase())
    .join(" ");
}

export function AppShell({
  user,
  notifications,
  unreadCount,
  children,
}: AppShellProps) {
  const pathname = usePathname();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [notificationsOpen, setNotificationsOpen] = useState(false);
  const isAdmin = user?.role === "SYSTEM_ADMIN";
  const isFinanceAdmin = user?.role === "FINANCE_ADMIN";

  const closeSidebar = () => setSidebarOpen(false);

  // When not authenticated, render children without the app shell
  if (!user) {
    return <>{children}</>;
  }

  return (
    <div className="shell">
      {/* Sidebar backdrop (mobile) */}
      <div
        className={`sidebar-backdrop ${sidebarOpen ? "sidebar-backdrop--open" : ""}`}
        onClick={closeSidebar}
        aria-hidden="true"
      />

      {/* Sidebar */}
      <aside
        className={`sidebar ${sidebarOpen ? "sidebar--open" : ""}`}
        aria-label="Main navigation"
      >
        <div className="sidebar__brand">
          <span className="sidebar__brand-mark" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
            </svg>
          </span>
          Financial Cashflow
        </div>

        <nav className="sidebar__nav">
          <div className="sidebar__nav-group">
            {mainNav.filter((item) => !item.roles || item.roles.includes(user.role)).map((item) => {
              const Icon = item.icon;
              const active = isActive(pathname, item.href);
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`sidebar__link ${active ? "sidebar__link--active" : ""}`}
                  onClick={closeSidebar}
                  aria-current={active ? "page" : undefined}
                >
                  <Icon size={18} />
                  {item.label}
                </Link>
              );
            })}
          </div>

          {isFinanceAdmin ? (
            <div className="sidebar__nav-group">
              {financeNav.map((item) => {
                const Icon = item.icon;
                const active = isActive(pathname, item.href);
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={`sidebar__link ${active ? "sidebar__link--active" : ""}`}
                    onClick={closeSidebar}
                    aria-current={active ? "page" : undefined}
                  >
                    <Icon size={18} />
                    {item.label}
                  </Link>
                );
              })}
            </div>
          ) : null}

          {isAdmin ? (
            <div className="sidebar__nav-group">
              <span className="sidebar__nav-label">Administration</span>
              {adminNav.map((item) => {
                const Icon = item.icon;
                const active = isActive(pathname, item.href);
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={`sidebar__link ${active ? "sidebar__link--active" : ""}`}
                    onClick={closeSidebar}
                    aria-current={active ? "page" : undefined}
                  >
                    <Icon size={18} />
                    {item.label}
                  </Link>
                );
              })}
            </div>
          ) : null}
        </nav>

        {user ? (
          <div className="sidebar__footer">
            <div className="sidebar__user">
              <span className="sidebar__avatar" aria-hidden="true">
                {getInitials(user.full_name)}
              </span>
              <div className="sidebar__user-info">
                <div className="sidebar__user-name">{user.full_name}</div>
                <div className="sidebar__user-role">{formatRole(user.role)}</div>
              </div>
            </div>
            <form action={signOut}>
              <button type="submit" className="sidebar__signout">
                <LogOut size={16} />
                Sign out
              </button>
            </form>
          </div>
        ) : null}
      </aside>

      {/* Main area */}
      <div className="main">
        <header className="topbar">
          <div className="topbar__left">
            <button
              type="button"
              className="topbar__menu-btn"
              onClick={() => setSidebarOpen(true)}
              aria-label="Open navigation menu"
            >
              <Menu size={22} />
            </button>
          </div>
          <div className="topbar__right">
            <div className="notifications-menu">
              <button
                type="button"
                className="topbar__icon-btn"
                aria-label={`Notifications${unreadCount > 0 ? `, ${unreadCount} unread` : ""}`}
                title="Notifications"
                aria-expanded={notificationsOpen}
                aria-controls="notifications-panel"
                onClick={() => setNotificationsOpen((open) => !open)}
              >
                <Bell size={22} />
                {unreadCount > 0 ? (
                  <span className="topbar__badge" aria-hidden="true">
                    {unreadCount > 99 ? "99+" : unreadCount}
                  </span>
                ) : null}
              </button>

              {notificationsOpen ? (
                <div
                  id="notifications-panel"
                  className="notifications-panel"
                  role="dialog"
                  aria-label="Notifications"
                >
                  <div className="notifications-panel__header">
                    <div>
                      <div className="notifications-panel__title">Notifications</div>
                      <div className="notifications-panel__meta">
                        {unreadCount} unread
                      </div>
                    </div>
                    {unreadCount > 0 ? (
                      <form action={markAllNotificationsRead}>
                        <button type="submit" className="btn-ghost btn-sm">
                          Mark all read
                        </button>
                      </form>
                    ) : null}
                  </div>

                  {notifications.length === 0 ? (
                    <p className="notifications-panel__empty">
                      No notifications yet.
                    </p>
                  ) : (
                    <ul className="notifications-list" role="list">
                      {notifications.map((notification) => (
                        <li
                          key={notification.id}
                          className={`notifications-list__item ${
                            notification.is_read ? "" : "notifications-list__item--unread"
                          }`}
                        >
                          <div className="notifications-list__content">
                            <div className="notifications-list__title">
                              {notification.title}
                            </div>
                            <p>{notification.message}</p>
                            <time dateTime={notification.created_at}>
                              {formatDateTime(notification.created_at)}
                            </time>
                          </div>
                          {!notification.is_read ? (
                            <form action={markNotificationRead}>
                              <input type="hidden" name="id" value={notification.id} />
                              <button type="submit" className="btn-ghost btn-sm">
                                Mark read
                              </button>
                            </form>
                          ) : null}
                        </li>
                      ))}
                    </ul>
                  )}

                  <Link
                    href="/notifications"
                    className="notifications-panel__view-all"
                    onClick={() => setNotificationsOpen(false)}
                  >
                    View all notifications
                  </Link>
                </div>
              ) : null}
            </div>
          </div>
        </header>

        <div className="main__content">{children}</div>
      </div>
    </div>
  );
}