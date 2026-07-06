import Link from "next/link";

import { createTransaction } from "@/app/actions";
import { TransactionForm } from "@/components/TransactionForm";
import { getCurrentUser } from "@/lib/current-user";
import { apiGet } from "@/lib/api";
import type {
  CashAccount,
  Category,
  Department,
  PaymentMethod,
} from "@/lib/types";
import { isFinanceRole } from "@/lib/types";

export default async function NewTransactionPage() {
  const user = await getCurrentUser();
  const [departments, categories, cashAccounts, paymentMethods] = await Promise.all([
    apiGet<Department[]>("/api/departments"),
    apiGet<Category[]>("/api/categories"),
    apiGet<CashAccount[]>("/api/cash-accounts"),
    apiGet<PaymentMethod[]>("/api/payment-methods"),
  ]);

  if (!user || (user.role !== "EMPLOYEE" && !isFinanceRole(user.role))) {
    return (
      <div className="container">
        <div className="empty">
          <div className="empty__title">Not available</div>
          <p className="empty__desc">Your role cannot create transactions.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <div className="page-header">
        <div>
          <h1>New transaction</h1>
          <p className="page-header__subtitle">
            Draft transactions can be edited before submission.
          </p>
        </div>
        <Link href="/transactions" className="btn-ghost">
          Back
        </Link>
      </div>

      <div className="section">
        <TransactionForm
          action={createTransaction}
          departments={departments}
          categories={categories}
          cashAccounts={cashAccounts}
          paymentMethods={paymentMethods}
          user={user}
          submitLabel="Create draft"
        />
      </div>
    </div>
  );
}