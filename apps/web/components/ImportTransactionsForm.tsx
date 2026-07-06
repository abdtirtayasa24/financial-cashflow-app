"use client";

import { useActionState } from "react";
import { AlertCircle } from "lucide-react";

import { importTransactions, type ImportActionResult } from "@/app/actions";

export function ImportTransactionsForm() {
  const [state, formAction] = useActionState<ImportActionResult | null, FormData>(
    importTransactions,
    null
  );

  return (
    <div className="card form-grid">
      <form action={formAction} aria-label="Import transactions" className="form-grid">
        <div className="field">
          <label htmlFor="file">CSV or Excel file</label>
          <input id="file" name="file" type="file" accept=".csv,.xlsx,text/csv,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" required />
          <p className="field__hint">Maximum 500 rows. Imported rows start as draft transactions.</p>
        </div>
        {state?.error ? <p className="error" role="alert"><AlertCircle size={16} />{state.error}</p> : null}
        <div className="form-actions"><button type="submit" className="btn-primary">Import transactions</button></div>
      </form>

      {state?.result ? (
        <div className="section" aria-live="polite">
          <h2 className="section__title">Import summary</h2>
          <div className="kpi-grid">
            <div className="kpi-card"><span className="kpi-card__label">Rows</span><strong className="tnum">{state.result.total_rows}</strong></div>
            <div className="kpi-card"><span className="kpi-card__label">Imported</span><strong className="tnum">{state.result.imported_count}</strong></div>
            <div className="kpi-card"><span className="kpi-card__label">Failed</span><strong className="tnum">{state.result.failed_count}</strong></div>
          </div>
          {state.result.errors.length > 0 ? (
            <div className="table-wrap">
              <table className="table">
                <thead><tr><th>Row</th><th>Error</th></tr></thead>
                <tbody>{state.result.errors.map((e) => <tr key={`${e.row_number}-${e.message}`}><td className="tnum">{e.row_number}</td><td>{e.message}</td></tr>)}</tbody>
              </table>
            </div>
          ) : null}
        </div>
      ) : null}
    </div>
  );
}
