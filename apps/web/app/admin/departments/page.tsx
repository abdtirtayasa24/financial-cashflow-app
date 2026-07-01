import {
  createDepartment,
  deleteDepartment,
  toggleDepartmentActive,
} from "@/app/actions";
import { DeleteButton } from "@/components/DeleteButton";
import { apiGet } from "@/lib/api";
import type { Department } from "@/lib/types";

export default async function DepartmentsPage() {
  const departments = await apiGet<Department[]>("/api/departments");

  return (
    <div className="container">
      <div className="page-header">
        <div>
          <h1>Departments</h1>
          <p className="page-header__subtitle">Manage departments and cost centers across the organization.</p>
        </div>
      </div>

      <div className="section">
        <form action={createDepartment} className="card form-grid" aria-label="Create department">
          <div className="form-row">
            <div className="field">
              <label htmlFor="name">Name</label>
              <input id="name" name="name" required placeholder="Operations" />
            </div>
            <div className="field">
              <label htmlFor="code">Code</label>
              <input id="code" name="code" required placeholder="OPS" />
            </div>
          </div>
          <div className="form-actions">
            <button type="submit" className="btn-primary">
              Add department
            </button>
          </div>
        </form>
      </div>

      <div className="section">
        <h2 className="section__title">All departments</h2>
        {departments.length === 0 ? (
          <div className="empty">
            <div className="empty__icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                <rect x="4" y="2" width="16" height="20" rx="2" />
                <path d="M9 22v-4h6v4" />
                <path d="M8 6h.01M16 6h.01M12 6h.01M8 10h.01M16 10h.01M12 10h.01M8 14h.01M16 14h.01M12 14h.01" />
              </svg>
            </div>
            <div className="empty__title">No departments yet</div>
            <p className="empty__desc">Add your first department to start organizing transactions by cost center.</p>
          </div>
        ) : (
          <div className="table-wrap">
            <table className="table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Code</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {departments.map((d) => (
                  <tr key={d.id}>
                    <td style={{ fontWeight: 500 }}>{d.name}</td>
                    <td className="text-secondary tnum">{d.code}</td>
                    <td>
                      <span className={`badge ${d.is_active ? "badge--active" : "badge--inactive"}`}>
                        <span className="badge__dot" aria-hidden="true" />
                        {d.is_active ? "Active" : "Inactive"}
                      </span>
                    </td>
                    <td>
                      <div className="row-actions">
                        <form action={toggleDepartmentActive}>
                          <input type="hidden" name="id" value={d.id} />
                          <input type="hidden" name="active" value={String(d.is_active)} />
                          <button type="submit" className="btn-ghost btn-sm">
                            {d.is_active ? "Deactivate" : "Activate"}
                          </button>
                        </form>
                        <DeleteButton action={deleteDepartment} id={d.id} label={d.name} />
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