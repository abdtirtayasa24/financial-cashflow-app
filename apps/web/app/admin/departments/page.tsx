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
      <h1>Departments</h1>

      <form action={createDepartment} className="card form-row" aria-label="Create department">
        <div className="field">
          <label htmlFor="name">Name</label>
          <input id="name" name="name" required />
        </div>
        <div className="field">
          <label htmlFor="code">Code</label>
          <input id="code" name="code" required />
        </div>
        <button type="submit" className="btn-primary">
          Add department
        </button>
      </form>

      {departments.length === 0 ? (
        <p className="empty">No departments yet.</p>
      ) : (
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
                <td>{d.name}</td>
                <td>{d.code}</td>
                <td>
                  <span className={`badge ${d.is_active ? "badge--active" : "badge--inactive"}`}>
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
      )}
    </div>
  );
}