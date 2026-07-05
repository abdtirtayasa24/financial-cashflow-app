import Link from "next/link";

import {
  markAllNotificationsRead,
  markNotificationRead,
} from "@/app/actions";
import { apiGet } from "@/lib/api";
import { formatDateTime } from "@/lib/format";
import type { AppNotification, UnreadCount } from "@/lib/types";

function notificationTypeLabel(type: string): string {
  return type
    .split("_")
    .map((part) => part.charAt(0) + part.slice(1).toLowerCase())
    .join(" ");
}

export default async function NotificationsPage() {
  const [notifications, unread] = await Promise.all([
    apiGet<AppNotification[]>("/api/notifications?limit=100"),
    apiGet<UnreadCount>("/api/notifications/unread-count"),
  ]);

  return (
    <div className="container">
      <div className="page-header">
        <div>
          <h1>Notifications</h1>
          <p className="page-header__subtitle">
            Review in-app alerts for pending approvals and generated drafts.
          </p>
        </div>
        {unread.count > 0 ? (
          <form action={markAllNotificationsRead}>
            <button type="submit" className="btn-primary">
              Mark all as read
            </button>
          </form>
        ) : null}
      </div>

      <div className="section">
        {notifications.length === 0 ? (
          <div className="empty">
            <div className="empty__title">No notifications yet</div>
            <p className="empty__desc">
              Notifications will appear here when transactions need attention.
            </p>
          </div>
        ) : (
          <ul className="notification-page-list" role="list">
            {notifications.map((notification) => (
              <li
                key={notification.id}
                className={`notification-card ${
                  notification.is_read ? "" : "notification-card--unread"
                }`}
              >
                <div className="notification-card__body">
                  <div className="notification-card__eyebrow">
                    {notificationTypeLabel(notification.type)} ·{" "}
                    {formatDateTime(notification.created_at)}
                  </div>
                  <h2>{notification.title}</h2>
                  <p>{notification.message}</p>
                  {notification.related_transaction_id ? (
                    <Link
                      href={`/transactions/${notification.related_transaction_id}`}
                      className="btn-ghost btn-sm"
                    >
                      View transaction
                    </Link>
                  ) : null}
                </div>
                {!notification.is_read ? (
                  <form action={markNotificationRead}>
                    <input type="hidden" name="id" value={notification.id} />
                    <button type="submit" className="btn-primary btn-sm">
                      Mark read
                    </button>
                  </form>
                ) : null}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
