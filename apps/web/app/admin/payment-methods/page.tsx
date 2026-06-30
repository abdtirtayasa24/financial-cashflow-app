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
      <h1>Payment Methods</h1>

      <form
        action={createPaymentMethod}
        className="card form-row"
        aria-label="Create payment method"
      >
        <div className="field">
          <label htmlFor="name">Name</label>
          <input id="name" name="name" required />
        </div>
        <button type="submit" className="btn-primary">
          Add payment method
        </button>
      </form>

      {methods.length === 0 ? (
        <p className="empty">No payment methods yet.</p>
      ) : (
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
                <td>{m.name}</td>
                <td>
                  <span className={`badge ${m.is_active ? "badge--active" : "badge--inactive"}`}>
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
      )}
    </div>
  );
}