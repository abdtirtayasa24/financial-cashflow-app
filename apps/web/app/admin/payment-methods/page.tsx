import {
  createPaymentMethod,
  deletePaymentMethod,
  togglePaymentMethodActive,
} from "@/app/actions";
import { DeleteButton } from "@/components/DeleteButton";
import { apiGet } from "@/lib/api";
import type { PaymentMethod } from "@/lib/types";

export default async function PaymentMethodsPage() {
  const methods = await apiGet<PaymentMethod[]>("/api/payment-methods");

  return (
    <div className="container">
      <div className="page-header">
        <div>
          <h1>Payment Methods</h1>
          <p className="page-header__subtitle">Configure how cash transactions are recorded.</p>
        </div>
      </div>

      <div className="section">
        <form
          action={createPaymentMethod}
          className="card form-grid"
          aria-label="Create payment method"
        >
          <div className="form-row">
            <div className="field">
              <label htmlFor="name">Name</label>
              <input id="name" name="name" required placeholder="Bank Transfer" />
            </div>
          </div>
          <div className="form-actions">
            <button type="submit" className="btn-primary">
              Add payment method
            </button>
          </div>
        </form>
      </div>

      <div className="section">
        <h2 className="section__title">All payment methods</h2>
        {methods.length === 0 ? (
          <div className="empty">
            <div className="empty__icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                <rect x="2" y="5" width="20" height="14" rx="2" />
                <line x1="2" y1="10" x2="22" y2="10" />
              </svg>
            </div>
            <div className="empty__title">No payment methods yet</div>
            <p className="empty__desc">Add payment methods like Cash, Bank Transfer, or E-Wallet.</p>
          </div>
        ) : (
          <div className="table-wrap">
            <table className="table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {methods.map((m) => (
                  <tr key={m.id}>
                    <td style={{ fontWeight: 500 }}>{m.name}</td>
                    <td>
                      <span className={`badge ${m.is_active ? "badge--active" : "badge--inactive"}`}>
                        <span className="badge__dot" aria-hidden="true" />
                        {m.is_active ? "Active" : "Inactive"}
                      </span>
                    </td>
                    <td>
                      <div className="row-actions">
                        <form action={togglePaymentMethodActive}>
                          <input type="hidden" name="id" value={m.id} />
                          <input type="hidden" name="active" value={String(m.is_active)} />
                          <button type="submit" className="btn-ghost btn-sm">
                            {m.is_active ? "Deactivate" : "Activate"}
                          </button>
                        </form>
                        <DeleteButton action={deletePaymentMethod} id={m.id} label={m.name} />
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