import {
  STATUS_BADGE_CLASS,
  STATUS_LABELS,
  type TransactionStatus,
} from "@/lib/types";

export function StatusBadge({ status }: { status: TransactionStatus }) {
  return (
    <span className={`badge ${STATUS_BADGE_CLASS[status]}`}>
      <span className="badge__dot" aria-hidden="true" />
      {STATUS_LABELS[status]}
    </span>
  );
}