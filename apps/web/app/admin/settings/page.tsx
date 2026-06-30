import { upsertAppSetting } from "@/app/actions";
import { apiGet } from "@/lib/api";
import type { AppSetting } from "@/lib/types";

export default async function SettingsPage() {
  const settings = await apiGet<AppSetting[]>("/api/settings");

  return (
    <div className="container">
      <h1>App Settings</h1>

      <form action={upsertAppSetting} className="card form-row" aria-label="Upsert setting">
        <div className="field">
          <label htmlFor="key">Key</label>
          <input id="key" name="key" required placeholder="attachment_threshold_amount" />
        </div>
        <div className="field">
          <label htmlFor="value">Value</label>
          <input id="value" name="value" required placeholder="5000000" />
        </div>
        <button type="submit" className="btn-primary">
          Save setting
        </button>
      </form>

      <h2>Current values</h2>
      {settings.length === 0 ? (
        <p className="empty">No settings configured.</p>
      ) : (
        <table className="table">
          <thead>
            <tr>
              <th>Key</th>
              <th>Value</th>
              <th>Updated at</th>
            </tr>
          </thead>
          <tbody>
            {settings.map((s) => (
              <tr key={s.id}>
                <td>{s.key}</td>
                <td>{s.value}</td>
                <td>{new Date(s.updated_at).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}