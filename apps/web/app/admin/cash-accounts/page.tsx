import { createCashAccount, deleteCashAccount } from "@/app/actions";
import { DeleteButton } from "@/components/DeleteButton";
import { apiGet } from "@/lib/api";
import type { CashAccount } from "@/lib/types";

export default async function CashAccountsPage() {
  const accounts = await apiGet<CashAccount[]>("/api/cash-accounts");

  return (
    <div className="container">
      <h1>Cash Accounts</h1>

      <form
        action={createCashAccount}
        className="card"
        aria-label="Create cash account"
        style={{ display: "grid", gap: "0.75rem" }}
      >
        <div className="field">
          <label htmlFor="name">Name</label>
          <input id="name" name="name" required />
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
        <button type="submit" className="btn-primary">
          Add cash account
        </button>
      </form>

      {accounts.length === 0 ? (
        <p className="empty">No cash accounts yet.</p>
      ) : (
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
                <td>{a.name}</td>
                <td>{a.account_type}</td>
                <td>{Number(a.opening_balance).toLocaleString("en-US")} {a.currency}</td>
                <td>
                  <span className={`badge ${a.is_active ? "badge--active" : "badge--inactive"}`}>
                    {a.is_active ? "Active" : "Inactive"}
                  </span>
                </td>
                <td>
                  <DeleteButton action={deleteCashAccount} id={a.id} label={a.name} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}