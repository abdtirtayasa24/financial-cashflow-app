import { createCashAccount, deleteCashAccount } from "@/app/actions";
import { DeleteButton } from "@/components/DeleteButton";
import { apiGet } from "@/lib/api";
import type { CashAccount } from "@/lib/types";

const ACCOUNT_TYPE_LABELS: Record<string, string> = {
  CASH: "Cash",
  BANK: "Bank",
  EWALLET: "E-Wallet",
  OTHER: "Other",
};

export default async function CashAccountsPage() {
  const accounts = await apiGet<CashAccount[]>("/api/cash-accounts");

  return (
    <div className="container">
      <div className="page-header">
        <div>
          <h1>Cash Accounts</h1>
          <p className="page-header__subtitle">Track cash positions across banks, cash, and e-wallets.</p>
        </div>
      </div>

      <div className="section">
        <form
          action={createCashAccount}
          className="card form-grid"
          aria-label="Create cash account"
        >
          <div className="field">
            <label htmlFor="name">Account name</label>
            <input id="name" name="name" required placeholder="BCA Operating Account" />
          </div>
          <div className="form-row">
            <div className="field">
              <label htmlFor="account_type">Type</label>
              <select id="account_type" name="account_type" required defaultValue="BANK">
                <option value="CASH">Cash</option>
                <option value="BANK">Bank</option>
                <option value="EWALLET">E-Wallet</option>
                <option value="OTHER">Other</option>
              </select>
            </div>
            <div className="field">
              <label htmlFor="opening_balance">Opening balance</label>
              <input
                id="opening_balance"
                name="opening_balance"
                type="number"
                step="0.01"
                min="0"
                defaultValue="0"
                required
                className="tnum"
              />
            </div>
            <div className="field">
              <label htmlFor="opening_balance_date">Opening balance date</label>
              <input
                id="opening_balance_date"
                name="opening_balance_date"
                type="date"
                required
              />
            </div>
          </div>
          <div className="form-actions">
            <button type="submit" className="btn-primary">
              Add cash account
            </button>
          </div>
        </form>
      </div>

      <div className="section">
        <h2 className="section__title">All cash accounts</h2>
        {accounts.length === 0 ? (
          <div className="empty">
            <div className="empty__icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M21 12V7H5a2 2 0 0 1 0-4h14v4" />
                <path d="M3 5v14a2 2 0 0 0 2 2h16v-5" />
                <path d="M18 12a2 2 0 0 0 0 4h4v-4Z" />
              </svg>
            </div>
            <div className="empty__title">No cash accounts yet</div>
            <p className="empty__desc">Add a bank, cash, or e-wallet account to start tracking balances.</p>
          </div>
        ) : (
          <div className="table-wrap">
            <table className="table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Type</th>
                  <th>Opening balance</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {accounts.map((a) => (
                  <tr key={a.id}>
                    <td style={{ fontWeight: 500 }}>{a.name}</td>
                    <td className="text-secondary">{ACCOUNT_TYPE_LABELS[a.account_type] ?? a.account_type}</td>
                    <td className="tnum text-secondary">
                      {Number(a.opening_balance).toLocaleString("en-US")} {a.currency}
                    </td>
                    <td>
                      <span className={`badge ${a.is_active ? "badge--active" : "badge--inactive"}`}>
                        <span className="badge__dot" aria-hidden="true" />
                        {a.is_active ? "Active" : "Inactive"}
                      </span>
                    </td>
                    <td>
                      <div className="row-actions">
                        <DeleteButton action={deleteCashAccount} id={a.id} label={a.name} />
                      </div>
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