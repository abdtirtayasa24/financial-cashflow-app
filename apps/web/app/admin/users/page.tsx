import { createUser, updateUser } from "@/app/actions";
import { apiGet } from "@/lib/api";
import type { Department, Role, User } from "@/lib/types";
import { ROLES } from "@/lib/types";

const STATUSES = ["ACTIVE", "INACTIVE"] as const;

export default async function UsersPage() {
  const [users, departments] = await Promise.all([
    apiGet<User[]>("/api/users"),
    apiGet<Department[]>("/api/departments"),
  ]);

  return (
    <div className="container">
      <h1>Users</h1>

      <form
        action={createUser}
        className="card"
        aria-label="Create user"
        style={{ display: "grid", gap: "0.75rem" }}
      >
        <div className="form-row">
          <div className="field">
            <label htmlFor="email">Email</label>
            <input id="email" name="email" type="email" required />
          </div>
          <div className="field">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              name="password"
              type="password"
              minLength={8}
              required
            />
          </div>
        </div>
        <div className="form-row">
          <div className="field">
            <label htmlFor="full_name">Full name</label>
            <input id="full_name" name="full_name" required />
          </div>
          <div className="field">
            <label htmlFor="role">Role</label>
            <select id="role" name="role" required defaultValue="EMPLOYEE">
              {ROLES.map((r) => (
                <option key={r} value={r}>
                  {r}
                </option>
              ))}
            </select>
          </div>
          <div className="field">
            <label htmlFor="department_id">Department</label>
            <select id="department_id" name="department_id" defaultValue="">
              <option value="">— None —</option>
              {departments.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.name}
                </option>
              ))}
            </select>
          </div>
        </div>
        <button type="submit" className="btn-primary">
          Create user
        </button>
      </form>

      <h2>Existing users</h2>
      {users.length === 0 ? (
        <p className="empty">No users yet.</p>
      ) : (
        <table className="table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Email</th>
              <th>Manage (role / department / status)</th>
            </tr>
          </thead>
          <tbody>
            {users.map((u) => (
              <tr key={u.id}>
                <td>{u.full_name}</td>
                <td>{u.email ?? "—"}</td>
                <td>
                  <form
                    action={updateUser}
                    aria-label={`Update user ${u.full_name}`}
                    style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap", alignItems: "flex-end" }}
                  >
                    <input type="hidden" name="id" value={u.id} />
                    <input type="hidden" name="full_name" value={u.full_name} />
                    <select name="role" defaultValue={u.role} aria-label="Role">
                      {ROLES.map((r: Role) => (
                        <option key={r} value={r}>
                          {r}
                        </option>
                      ))}
                    </select>
                    <select
                      name="department_id"
                      defaultValue={u.department_id ?? ""}
                      aria-label="Department"
                    >
                      <option value="">— None —</option>
                      {departments.map((d) => (
                        <option key={d.id} value={d.id}>
                          {d.name}
                        </option>
                      ))}
                    </select>
                    <select name="status" defaultValue={u.status} aria-label="Status">
                      {STATUSES.map((s) => (
                        <option key={s} value={s}>
                          {s}
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
      )}
    </div>
  );
}