import Link from "next/link";

import { deleteAttachment, deleteTransaction } from "@/app/actions";
import { ConfirmButton } from "@/components/ConfirmButton";
import { StatusBadge } from "@/components/StatusBadge";
import { SubmitForm } from "@/components/SubmitForm";
import { UploadForm } from "@/components/UploadForm";
import { apiGet } from "@/lib/api";
import { getCurrentUser } from "@/lib/current-user";
import { formatBytes, formatDate, formatDateTime, formatIDR } from "@/lib/format";
import type {
  Attachment,
  AuditLog,
  CashAccount,
  Category,
  Department,
  PaymentMethod,
  Transaction,
} from "@/lib/types";

function DetailRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="detail__row">
      <dt className="detail__label">{label}</dt>
      <dd className="detail__value">{value}</dd>
    </div>
  );
}

function auditActionLabel(action: string): string {
  const map: Record<string, string> = {
    CREATE: "Created",
    UPDATE: "Edited",
    SUBMIT: "Submitted",
    DELETE: "Deleted",
    ATTACHMENT_ADD: "Attachment added",
    ATTACHMENT_REMOVE: "Attachment removed",
    APPROVE: "Approved",
    REJECT: "Rejected",
    VOID: "Voided",
  };
  return map[action] ?? action;
}

export default async function TransactionDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const user = await getCurrentUser();

  let tx: Transaction;
  try {
    tx = await apiGet<Transaction>(`/api/transactions/${id}`);
  } catch {
    return (
      <div className="container">
        <div className="empty">
          <div className="empty__title">Transaction not found</div>
          <p className="empty__desc">
            This transaction may have been deleted, or you do not have access to it.
          </p>
        </div>
      </div>
    );
  }

  const [attachments, auditLogs, departments, categories, cashAccounts, paymentMethods] =
    await Promise.all([
      apiGet<Attachment[]>(`/api/transactions/${id}/attachments`).catch(() => []),
      apiGet<AuditLog[]>(`/api/transactions/${id}/audit-logs`).catch(() => []),
      apiGet<Department[]>("/api/departments"),
      apiGet<Category[]>("/api/categories"),
      apiGet<CashAccount[]>("/api/cash-accounts"),
      apiGet<PaymentMethod[]>("/api/payment-methods"),
    ]);

  const nameOf = (list: { id: string; name: string }[], idVal: string | null) =>
    idVal ? (list.find((x) => x.id === idVal)?.name ?? "—") : "—";

  const isMutableStatus = tx.status === "DRAFT" || tx.status === "REJECTED";
  const canMutate =
    isMutableStatus &&
    user != null &&
    (user.role === "FINANCE_ADMIN" ||
      (user.role === "EMPLOYEE" && tx.created_by === user.id));

  return (
    <div className="container">
      <div className="page-header">
        <div>
          <h1 className="tnum">{tx.transaction_no}</h1>
          <p className="page-header__subtitle">
            <StatusBadge status={tx.status} />{" "}
            <span className="text-secondary">
              {tx.direction === "INFLOW" ? "Inflow" : "Outflow"} ·{" "}
              {formatDate(tx.transaction_date)}
            </span>
          </p>
        </div>
        <Link href="/transactions" className="btn-ghost">
          Back
        </Link>
      </div>

      {canMutate ? (
        <div className="action-bar section">
          <Link href={`/transactions/${id}/edit`} className="btn-primary">
            Edit
          </Link>
          <SubmitForm id={id} />
          <ConfirmButton
            action={deleteTransaction}
            id={id}
            label={tx.transaction_no}
            confirmLabel="Confirm delete"
          />
        </div>
      ) : null}

      <div className="section">
        <div className="card">
          <dl className="detail">
            <DetailRow label="Amount" value={formatIDR(tx.amount)} />
            <DetailRow label="Base amount" value={formatIDR(tx.base_amount)} />
            <DetailRow label="Currency" value={tx.currency} />
            <DetailRow label="Direction" value={tx.direction === "INFLOW" ? "Inflow" : "Outflow"} />
            <DetailRow label="Department" value={nameOf(departments, tx.department_id)} />
            <DetailRow label="Category" value={nameOf(categories, tx.category_id)} />
            <DetailRow label="Cash account" value={nameOf(cashAccounts, tx.cash_account_id)} />
            <DetailRow label="Payment method" value={nameOf(paymentMethods, tx.payment_method_id)} />
            <DetailRow label="Counterparty" value={tx.counterparty_name ?? "—"} />
            <DetailRow label="Reference no." value={tx.reference_no ?? "—"} />
            <DetailRow label="Description" value={tx.description ?? "—"} />
            <DetailRow label="Submitted at" value={formatDateTime(tx.submitted_at)} />
            {tx.rejection_reason ? (
              <DetailRow label="Rejection reason" value={tx.rejection_reason} />
            ) : null}
            {tx.void_reason ? (
              <DetailRow label="Void reason" value={tx.void_reason} />
            ) : null}
            <DetailRow label="Created at" value={formatDateTime(tx.created_at)} />
            <DetailRow label="Updated at" value={formatDateTime(tx.updated_at)} />
          </dl>
        </div>
      </div>

      <div className="section">
        <h2 className="section__title">Attachments</h2>
        {attachments.length === 0 ? (
          <p className="text-secondary text-sm">No attachments.</p>
        ) : (
          <ul className="attachment-list" role="list">
            {attachments.map((a) => (
              <li key={a.id} className="attachment-list__item">
                <Link
                  href={`/transactions/${id}/attachments/${a.id}/download`}
                  className="attachment-list__link"
                >
                  {a.original_file_name}
                </Link>
                <span className="text-tertiary text-sm">
                  {formatBytes(a.file_size_bytes)} · {formatDateTime(a.uploaded_at)}
                </span>
                {canMutate ? (
                  <ConfirmButton
                    action={deleteAttachment}
                    id={id}
                    extraFields={{ attachmentId: a.id }}
                    label={a.original_file_name}
                    confirmLabel="Remove"
                  />
                ) : null}
              </li>
            ))}
          </ul>
        )}
        {canMutate ? <UploadForm id={id} /> : null}
      </div>

      <div className="section">
        <h2 className="section__title">Audit trail</h2>
        {auditLogs.length === 0 ? (
          <p className="text-secondary text-sm">No audit entries.</p>
        ) : (
          <div className="table-wrap">
            <table className="table">
              <thead>
                <tr>
                  <th>Action</th>
                  <th>Actor</th>
                  <th>When</th>
                  <th>Details</th>
                </tr>
              </thead>
              <tbody>
                {auditLogs.map((log) => (
                  <tr key={log.id}>
                    <td style={{ fontWeight: 500 }}>{auditActionLabel(log.action)}</td>
                    <td className="text-secondary">{log.actor_name ?? "—"}</td>
                    <td className="text-secondary">{formatDateTime(log.created_at)}</td>
                    <td className="text-tertiary text-sm audit-detail">
                      {log.old_value ? (
                        <span>from {JSON.stringify(log.old_value)}</span>
                      ) : null}
                      {log.old_value && log.new_value ? " " : null}
                      {log.new_value ? (
                        <span>to {JSON.stringify(log.new_value)}</span>
                      ) : null}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}