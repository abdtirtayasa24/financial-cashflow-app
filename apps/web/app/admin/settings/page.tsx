import { updateAttachmentThresholdSettings, upsertAppSetting } from "@/app/actions";
import { apiGet } from "@/lib/api";
import type { AppSetting } from "@/lib/types";

export default async function SettingsPage() {
  const settings = await apiGet<AppSetting[]>("/api/settings");
  const byKey = new Map(settings.map((s) => [s.key, s.value]));
  const thresholdEnabled = byKey.get("attachment_threshold_enabled") !== "false";
  const thresholdAmount = byKey.get("attachment_threshold_amount") ?? "5000000";

  return (
    <div className="container">
      <div className="page-header">
        <div>
          <h1>App Settings</h1>
          <p className="page-header__subtitle">Configure application-wide parameters and thresholds.</p>
        </div>
      </div>

      <div className="section">
        <h2 className="section__title">Attachment threshold</h2>
        <form action={updateAttachmentThresholdSettings} className="card form-grid" aria-label="Attachment threshold settings">
          <div className="form-row">
            <div className="field">
              <label htmlFor="attachment_threshold_enabled">Require attachments above threshold</label>
              <select id="attachment_threshold_enabled" name="attachment_threshold_enabled" defaultValue={thresholdEnabled ? "on" : "off"}>
                <option value="on">Enabled</option>
                <option value="off">Disabled</option>
              </select>
            </div>
            <div className="field">
              <label htmlFor="attachment_threshold_amount">Threshold amount (IDR)</label>
              <input id="attachment_threshold_amount" name="attachment_threshold_amount" type="number" min="0.01" step="0.01" required className="tnum" defaultValue={thresholdAmount} />
            </div>
          </div>
          <div className="form-actions">
            <button type="submit" className="btn-primary">Save threshold settings</button>
          </div>
        </form>
      </div>

      <div className="section">
        <h2 className="section__title">Advanced key/value settings</h2>
        <form action={upsertAppSetting} className="card form-grid" aria-label="Add or update setting">
          <div className="form-row">
            <div className="field">
              <label htmlFor="key">Key</label>
              <input id="key" name="key" required placeholder="attachment_threshold_amount" />
            </div>
            <div className="field">
              <label htmlFor="value">Value</label>
              <input id="value" name="value" required placeholder="5000000" />
            </div>
          </div>
          <div className="form-actions">
            <button type="submit" className="btn-primary">
              Save setting
            </button>
          </div>
        </form>
      </div>

      <div className="section">
        <h2 className="section__title">Current values</h2>
        {settings.length === 0 ? (
          <div className="empty">
            <div className="empty__icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="3" />
                <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z" />
              </svg>
            </div>
            <div className="empty__title">No settings configured</div>
            <p className="empty__desc">Add configuration keys to control application behavior.</p>
          </div>
        ) : (
          <div className="table-wrap">
            <table className="table">
              <thead>
                <tr>
                  <th>Key</th>
                  <th>Value</th>
                  <th>Updated</th>
                </tr>
              </thead>
              <tbody>
                {settings.map((s) => (
                  <tr key={s.id}>
                    <td className="text-secondary" style={{ fontFamily: "var(--font-mono)", fontSize: "var(--text-xs)" }}>
                      {s.key}
                    </td>
                    <td style={{ fontWeight: 500 }}>{s.value}</td>
                    <td className="text-secondary text-sm">
                      {new Date(s.updated_at).toLocaleString()}
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