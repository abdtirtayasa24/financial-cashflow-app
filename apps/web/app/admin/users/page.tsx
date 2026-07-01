import { createUser, updateUser } from "@/app/actions";
import { apiGet } from "@/lib/api";
import type { Department, Role, User } from "@/lib/types";
import { ROLES } from "@/lib/types";

const STATUSES = ["ACTIVE", "INACTIVE"] as const;

function formatRole(role: string): string {
  return role
    .split("_")
    .map((w) => w.charAt(0) + w.slice(1).toLowerCase())
    .join(" ");
}

export default async function UsersPage() {
  const [users, departments] = await Promise.all([
    apiGet<User[]>("/api/users"),
    apiGet<Department[]>("/api/departments"),
  ]);

  return (
    <div className="container">
      <div className="page-header">
        <div>
          <h1>Users</h1>
          <p className="page-header__subtitle">Manage user accounts, roles, and department assignments.</p>
        </div>
      </div>

      <div className="section">
        <form action={createUser} className="card form-grid" aria-label="Create user">
          <div className="form-row">
            <div className="field">
              <label htmlFor="email">Email</label>
              <input id="email" name="email" type="email" required placeholder="user@company.com" />
            </div>
            <div className="field">
              <label htmlFor="password">Password</label>
              <input id="password" name="password" type="password" minLength={8} required placeholder="Min. 8 characters" />
            </div>
          </div>
          <div className="form-row">
            <div className="field">
              <label htmlFor="full_name">Full name</label>
              <input id="full_name" name="full_name" required placeholder="John Doe" />
            </div>
            <div className="field">
              <label htmlFor="role">Role</label>
              <select id="role" name="role" required defaultValue="EMPLOYEE">
                {ROLES.map((r) => (
                  <option key={r} value={r}>
                    {formatRole(r)}
                  </option>
                ))}
              </select>
            </div>
            <div className="field">
              <label htmlFor="department_id">Department</label>
              <select id="department_id" name="department_id" defaultValue="">
                <option value="">None</option>
                {departments.map((d) => (
                  <option key={d.id} value={d.id}>
                    {d.name}
                  </option>
                ))}
              </select>
            </div>
          </div>
          <div className="form-actions">
            <button type="submit" className="btn-primary">
              Create user
            </button>
          </div>
        </form>
      </div>

      <div className="section">
        <h2 className="section__title">All users</h2>
        {users.length === 0 ? (
          <div className="empty">
            <div className="empty__icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
                <circle cx="9" cy="7" r="4" />
                <path d="M22 21v-2a4 4 0 0 0-3-3.87" />
                <path d="M16 3.13a4 4 0 0 1 0 7.75" />
              </svg>
            </div>
            <div className="empty__title">No users yet</div>
            <p className="empty__desc">Create your first user using the form above.</p>
          </div>
        ) : (
          <div className="table-wrap">
            <table className="table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Email</th>
                  <th>Role / Department / Status</th>
                </tr>
              </thead>
              <tbody>
                {users.map((u) => (
                  <tr key={u.id}>
                    <td style={{ fontWeight: 500 }}>{u.full_name}</td>
                    <td className="text-secondary">{u.email ?? "—"}</td>
                    <td>
                      <form
                        action={updateUser}
                        aria-label={`Update user ${u.full_name}`}
                        style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap", alignItems: "flex-end" }}
                      >
                        <input type="hidden" name="id" value={u.id} />
                        <input type="hidden" name="full_name" value={u.full_name} />
                        <select name="role" defaultValue={u.role} aria-label="Role" className="btn-sm" style={{ width: "auto", minHeight: "30px" }}>
                          {ROLES.map((r: Role) => (
                            <option key={r} value={r}>
                              {formatRole(r)}
                            </option>
                          ))}
                        </select>
                        <select
                          name="department_id"
                          defaultValue={u.department_id ?? ""}
                          aria-label="Department"
                          className="btn-sm"
                          style={{ width: "auto", minHeight: "30px" }}
                        >
                          <option value="">None</option>
                          {departments.map((d) => (
                            <option key={d.id} value={d.id}>
                              {d.name}
                            </option>
                          ))}
                        </select>
                        <select name="status" defaultValue={u.status} aria-label="Status" className="btn-sm" style={{ width: "auto", minHeight: "30px" }}>
                          {STATUSES.map((s) => (
                            <option key={s} value={s}>
                              {s.charAt(0) + s.slice(1).toLowerCase()}
                            </option>
                          ))}
                        </select>
                        <button type="submit" className="btn-primary btn-sm">
                          Save
                        </button>
                      </form>
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