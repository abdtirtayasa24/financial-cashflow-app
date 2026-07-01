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
  Transaction,
  TransactionDirection,
} from "@/lib/types";
import { DIRECTIONS } from "@/lib/types";

interface TransactionFormProps {
  action: (prev: ActionResult | null, formData: FormData) => Promise<ActionResult>;
  departments: Department[];
  categories: Category[];
  cashAccounts: CashAccount[];
  paymentMethods: PaymentMethod[];
  user: CurrentUser;
  initial?: Partial<Transaction>;
  submitLabel?: string;
}

function opt(value: string | null | undefined): string {
  return value ?? "";
}

export function TransactionForm({
  action,
  departments,
  categories,
  cashAccounts,
  paymentMethods,
  user,
  initial,
  submitLabel = "Save transaction",
}: TransactionFormProps) {
  const [state, formAction] = useActionState(action, null);
  const [direction, setDirection] = useState<TransactionDirection>(
    (initial?.direction as TransactionDirection) ?? "INFLOW"
  );

  const isEmployee = user.role === "EMPLOYEE";
  const editableDepartments = isEmployee
    ? departments.filter((d) => d.id === user.department_id)
    : departments;

  const availableCategories = useMemo(
    () =>
      categories.filter(
        (c) => c.direction === direction || c.direction === "BOTH"
      ),
    [categories, direction]
  );

  return (
    <form action={formAction} className="card form-grid" aria-label="Transaction form">
      {initial?.id ? <input type="hidden" name="id" value={initial.id} /> : null}

      <div className="form-row">
        <div className="field">
          <label htmlFor="transaction_date">Transaction date</label>
          <input
            id="transaction_date"
            name="transaction_date"
            type="date"
            required
            defaultValue={opt(initial?.transaction_date)}
          />
        </div>
        <div className="field">
          <label htmlFor="direction">Direction</label>
          <select
            id="direction"
            name="direction"
            required
            value={direction}
            onChange={(e) => setDirection(e.target.value as TransactionDirection)}
          >
            {DIRECTIONS.map((d) => (
              <option key={d} value={d}>
                {d === "INFLOW" ? "Inflow" : "Outflow"}
              </option>
            ))}
          </select>
        </div>
        <div className="field">
          <label htmlFor="amount">Amount (IDR)</label>
          <input
            id="amount"
            name="amount"
            type="number"
            step="0.01"
            min="0.01"
            required
            inputMode="decimal"
            className="tnum"
            defaultValue={opt(initial?.amount != null ? String(initial.amount) : undefined)}
          />
        </div>
      </div>

      <div className="form-row">
        <div className="field">
          <label htmlFor="department_id">Department</label>
          {isEmployee ? (
            <>
              <input
                type="hidden"
                name="department_id"
                value={user.department_id ?? ""}
              />
              <select disabled aria-label="Department (fixed)">
                {editableDepartments.map((d) => (
                  <option key={d.id}>{d.name}</option>
                ))}
              </select>
            </>
          ) : (
            <select
              id="department_id"
              name="department_id"
              required
              defaultValue={opt(initial?.department_id)}
            >
              {departments.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.name}
                </option>
              ))}
            </select>
          )}
        </div>
        <div className="field">
          <label htmlFor="category_id">Category</label>
          <select
            id="category_id"
            name="category_id"
            required
            defaultValue={opt(initial?.category_id)}
          >
            {availableCategories.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>
        </div>
        <div className="field">
          <label htmlFor="cash_account_id">Cash account</label>
          <select
            id="cash_account_id"
            name="cash_account_id"
            required
            defaultValue={opt(initial?.cash_account_id)}
          >
            {cashAccounts.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>
        </div>
        <div className="field">
          <label htmlFor="payment_method_id">Payment method</label>
          <select
            id="payment_method_id"
            name="payment_method_id"
            required
            defaultValue={opt(initial?.payment_method_id)}
          >
            {paymentMethods.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="form-row">
        <div className="field">
          <label htmlFor="counterparty_name">Counterparty</label>
          <input
            id="counterparty_name"
            name="counterparty_name"
            placeholder="Vendor / customer name"
            defaultValue={opt(initial?.counterparty_name)}
          />
        </div>
        <div className="field">
          <label htmlFor="reference_no">Reference no.</label>
          <input
            id="reference_no"
            name="reference_no"
            placeholder="Invoice / receipt no."
            defaultValue={opt(initial?.reference_no)}
          />
        </div>
      </div>

      <div className="field">
        <label htmlFor="description">Description</label>
        <textarea
          id="description"
          name="description"
          rows={3}
          placeholder="Optional notes"
          defaultValue={opt(initial?.description)}
        />
      </div>

      {state?.error ? (
        <p className="error" role="alert">
          <AlertCircle size={16} />
          {state.error}
        </p>
      ) : null}

      <div className="form-actions">
        <button type="submit" className="btn-primary">
          {submitLabel}
        </button>
      </div>
    </form>
  );
}