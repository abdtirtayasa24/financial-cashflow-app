import Link from "next/link";

import { updateTransaction } from "@/app/actions";
import { TransactionForm } from "@/components/TransactionForm";
import { apiGet } from "@/lib/api";
import { getCurrentUser } from "@/lib/current-user";
import type {
  CashAccount,
  Category,
  Department,
  PaymentMethod,
  Transaction,
} from "@/lib/types";

export default async function EditTransactionPage({
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

  const isMutableStatus = tx.status === "DRAFT" || tx.status === "REJECTED";
  const canMutate =
    isMutableStatus &&
    user != null &&
    (user.role === "FINANCE_ADMIN" ||
      (user.role === "EMPLOYEE" && tx.created_by === user.id));

  if (!canMutate) {
    return (
      <div className="container">
        <div className="empty">
          <div className="empty__title">Not editable</div>
          <p className="empty__desc">
            Only DRAFT or REJECTED transactions you own can be edited.
          </p>
        </div>
        <div className="section">
          <Link href={`/transactions/${id}`} className="btn-ghost">
            Back to transaction
          </Link>
        </div>
      </div>
    );
  }

  const [departments, categories, cashAccounts, paymentMethods] = await Promise.all([
    apiGet<Department[]>("/api/departments"),
    apiGet<Category[]>("/api/categories"),
    apiGet<CashAccount[]>("/api/cash-accounts"),
    apiGet<PaymentMethod[]>("/api/payment-methods"),
  ]);

  return (
    <div className="container">
      <div className="page-header">
        <div>
          <h1>Edit transaction</h1>
          <p className="page-header__subtitle tnum">{tx.transaction_no}</p>
        </div>
        <Link href={`/transactions/${id}`} className="btn-ghost">
          Cancel
        </Link>
      </div>

      <div className="section">
        <TransactionForm
          action={updateTransaction}
          departments={departments}
          categories={categories}
          cashAccounts={cashAccounts}
          paymentMethods={paymentMethods}
          user={user!}
          initial={tx}
          submitLabel="Save changes"
        />
      </div>
    </div>
  );
}