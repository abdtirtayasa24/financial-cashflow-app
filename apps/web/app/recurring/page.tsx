import { deactivateRecurringTemplate, updateRecurringTemplate, createRecurringTemplate } from "@/app/actions";
import { RecurringTemplateForm } from "@/components/RecurringTemplateForm";
import { apiGet } from "@/lib/api";
import { getCurrentUser } from "@/lib/current-user";
import type { CashAccount, Category, Department, PaymentMethod, RecurringTemplate } from "@/lib/types";
import { isFinanceRole } from "@/lib/types";

function nameById<T extends { id: string; name: string }>(items: T[], id: string | null | undefined): string {
  return items.find((item) => item.id === id)?.name ?? "—";
}

export default async function RecurringPage() {
  const user = await getCurrentUser();
  if (!user || !["FINANCE_ADMIN", "MANAGEMENT", "EMPLOYEE", "DEPARTMENT_MANAGER"].includes(user.role)) {
    return <div className="container"><div className="empty"><div className="empty__title">Not available</div><p className="empty__desc">Your role cannot access recurring templates.</p></div></div>;
  }

  const [templates, departments, categories, cashAccounts, paymentMethods] = await Promise.all([
    apiGet<RecurringTemplate[]>("/api/recurring-templates"),
    apiGet<Department[]>("/api/departments"),
    apiGet<Category[]>("/api/categories"),
    apiGet<CashAccount[]>("/api/cash-accounts"),
    apiGet<PaymentMethod[]>("/api/payment-methods"),
  ]);
  const canMutate = isFinanceRole(user.role) || user.role === "EMPLOYEE";
  const canManageTemplate = (template: RecurringTemplate): boolean => {
    if (!template.is_active) return false;
    if (isFinanceRole(user.role)) return true;
    return (
      user.role === "EMPLOYEE" &&
      template.created_by === user.id &&
      template.submission_mode === "DRAFT"
    );
  };

  return (
    <div className="container">
      <div className="page-header"><div><h1>Recurring transactions</h1><p className="page-header__subtitle">Manage scheduled transaction templates. Generated transactions still require normal approval.</p></div></div>

      {canMutate ? (
        <div className="section">
          <h2 className="section__title">Create template</h2>
          <RecurringTemplateForm action={createRecurringTemplate} departments={departments} categories={categories} cashAccounts={cashAccounts} paymentMethods={paymentMethods} user={user} submitLabel="Create template" />
        </div>
      ) : null}

      <div className="section">
        <h2 className="section__title">Templates</h2>
        {templates.length === 0 ? (
          <div className="empty"><div className="empty__title">No recurring templates</div><p className="empty__desc">Create a template for repeated cashflow events.</p></div>
        ) : (
          <div className="table-wrap">
            <table className="table">
              <thead><tr><th>Schedule</th><th>Template</th><th>Amount</th><th>Mode</th><th>Status</th><th>Actions</th></tr></thead>
              <tbody>{templates.map((t) => (
                <tr key={t.id}>
                  <td><div>{t.frequency} / every {t.interval}</div><div className="text-secondary text-sm">Next: {t.next_run_date}</div></td>
                  <td><div style={{ fontWeight: 500 }}>{nameById(departments, t.department_id)} · {nameById(categories, t.category_id)}</div><div className="text-secondary text-sm">{nameById(cashAccounts, t.cash_account_id)}</div></td>
                  <td className="tnum">{Number(t.amount).toLocaleString("en-US")} IDR</td>
                  <td>{t.submission_mode === "AUTO_SUBMIT" ? "Auto-submit" : "Draft"}</td>
                  <td><span className={`badge ${t.is_active ? "badge--active" : "badge--inactive"}`}><span className="badge__dot" aria-hidden="true" />{t.is_active ? "Active" : "Inactive"}</span></td>
                  <td>{canManageTemplate(t) ? <div className="row-actions"><details><summary className="btn-ghost btn-sm">Edit</summary><div style={{ marginTop: "var(--space-3)", minWidth: 420 }}><RecurringTemplateForm action={updateRecurringTemplate} departments={departments} categories={categories} cashAccounts={cashAccounts} paymentMethods={paymentMethods} user={user} initial={t} submitLabel="Save" /></div></details><form action={deactivateRecurringTemplate}><input type="hidden" name="id" value={t.id} /><button type="submit" className="btn-danger btn-sm">Deactivate</button></form></div> : "—"}</td>
                </tr>
              ))}</tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
