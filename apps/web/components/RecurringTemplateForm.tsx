"use client";

import { useActionState, useMemo, useState } from "react";
import { AlertCircle } from "lucide-react";

import type { ActionResult } from "@/app/actions";
import type {
  CashAccount,
  Category,
  CurrentUser,
  Department,
  PaymentMethod,
  RecurringTemplate,
  TransactionDirection,
} from "@/lib/types";
import { DIRECTIONS } from "@/lib/types";

interface Props {
  action: (prev: ActionResult | null, formData: FormData) => Promise<ActionResult>;
  departments: Department[];
  categories: Category[];
  cashAccounts: CashAccount[];
  paymentMethods: PaymentMethod[];
  user: CurrentUser;
  initial?: Partial<RecurringTemplate>;
  submitLabel: string;
}

function opt(value: string | number | null | undefined): string {
  return value == null ? "" : String(value);
}

export function RecurringTemplateForm({
  action,
  departments,
  categories,
  cashAccounts,
  paymentMethods,
  user,
  initial,
  submitLabel,
}: Props) {
  const [state, formAction] = useActionState(action, null);
  const [direction, setDirection] = useState<TransactionDirection>(
    initial?.direction ?? "OUTFLOW"
  );
  const isEmployee = user.role === "EMPLOYEE";
  const canAutoSubmit = user.role === "FINANCE_ADMIN";
  const editableDepartments = isEmployee
    ? departments.filter((d) => d.id === user.department_id)
    : departments;
  const availableCategories = useMemo(
    () => categories.filter((c) => c.direction === direction || c.direction === "BOTH"),
    [categories, direction]
  );

  return (
    <form action={formAction} className="card form-grid" aria-label="Recurring template form">
      {initial?.id ? <input type="hidden" name="id" value={initial.id} /> : null}
      <div className="form-row">
        <div className="field">
          <label htmlFor="department_id">Department</label>
          {isEmployee ? (
            <>
              <input type="hidden" name="department_id" value={user.department_id ?? ""} />
              <select disabled aria-label="Department (fixed)">
                {editableDepartments.map((d) => <option key={d.id}>{d.name}</option>)}
              </select>
            </>
          ) : (
            <select id="department_id" name="department_id" required defaultValue={opt(initial?.department_id)}>
              {departments.map((d) => <option key={d.id} value={d.id}>{d.name}</option>)}
            </select>
          )}
        </div>
        <div className="field">
          <label htmlFor="submission_mode">Submission mode</label>
          <select id="submission_mode" name="submission_mode" required defaultValue={initial?.submission_mode ?? "DRAFT"}>
            <option value="DRAFT">Draft / reminder</option>
            {canAutoSubmit ? <option value="AUTO_SUBMIT">Auto-submit</option> : null}
          </select>
        </div>
        <div className="field">
          <label htmlFor="direction">Direction</label>
          <select id="direction" name="direction" required value={direction} onChange={(e) => setDirection(e.target.value as TransactionDirection)}>
            {DIRECTIONS.map((d) => <option key={d} value={d}>{d === "INFLOW" ? "Inflow" : "Outflow"}</option>)}
          </select>
        </div>
        <div className="field">
          <label htmlFor="amount">Amount (IDR)</label>
          <input id="amount" name="amount" type="number" min="0.01" step="0.01" required className="tnum" defaultValue={opt(initial?.amount)} />
        </div>
      </div>

      <div className="form-row">
        <div className="field">
          <label htmlFor="category_id">Category</label>
          <select id="category_id" name="category_id" required defaultValue={opt(initial?.category_id)}>
            {availableCategories.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
          </select>
        </div>
        <div className="field">
          <label htmlFor="cash_account_id">Cash account</label>
          <select id="cash_account_id" name="cash_account_id" required defaultValue={opt(initial?.cash_account_id)}>
            {cashAccounts.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
          </select>
        </div>
        <div className="field">
          <label htmlFor="payment_method_id">Payment method</label>
          <select id="payment_method_id" name="payment_method_id" required defaultValue={opt(initial?.payment_method_id)}>
            {paymentMethods.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
          </select>
        </div>
      </div>

      <div className="form-row">
        <div className="field">
          <label htmlFor="frequency">Frequency</label>
          <select id="frequency" name="frequency" required defaultValue={initial?.frequency ?? "MONTHLY"}>
            <option value="DAILY">Daily</option>
            <option value="WEEKLY">Weekly</option>
            <option value="MONTHLY">Monthly</option>
          </select>
        </div>
        <div className="field">
          <label htmlFor="interval">Interval</label>
          <input id="interval" name="interval" type="number" min="1" required defaultValue={opt(initial?.interval ?? 1)} />
        </div>
        <div className="field">
          <label htmlFor="next_run_date">Next run date</label>
          <input id="next_run_date" name="next_run_date" type="date" required defaultValue={opt(initial?.next_run_date)} />
        </div>
        <div className="field">
          <label htmlFor="end_date">End date</label>
          <input id="end_date" name="end_date" type="date" defaultValue={opt(initial?.end_date)} />
        </div>
      </div>

      <div className="form-row">
        <div className="field">
          <label htmlFor="counterparty_name">Counterparty</label>
          <input id="counterparty_name" name="counterparty_name" defaultValue={opt(initial?.counterparty_name)} />
        </div>
        <div className="field">
          <label htmlFor="reference_no">Reference no.</label>
          <input id="reference_no" name="reference_no" defaultValue={opt(initial?.reference_no)} />
        </div>
      </div>
      <div className="field">
        <label htmlFor="description">Description</label>
        <textarea id="description" name="description" rows={3} defaultValue={opt(initial?.description)} />
      </div>

      {state?.error ? <p className="error" role="alert"><AlertCircle size={16} />{state.error}</p> : null}
      <div className="form-actions"><button className="btn-primary" type="submit">{submitLabel}</button></div>
    </form>
  );
}
