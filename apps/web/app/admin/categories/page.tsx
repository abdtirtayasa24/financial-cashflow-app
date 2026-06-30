import {
  createCategory,
  deleteCategory,
  toggleCategoryActive,
} from "@/app/actions";
import { DeleteButton } from "@/components/DeleteButton";
import { apiGet } from "@/lib/api";
import type { Category } from "@/lib/types";

export default async function CategoriesPage() {
  const categories = await apiGet<Category[]>("/api/categories");

  return (
    <div className="container">
      <h1>Cashflow Categories</h1>

      <form action={createCategory} className="card form-row" aria-label="Create category">
        <div className="field">
          <label htmlFor="name">Name</label>
          <input id="name" name="name" required />
        </div>
        <div className="field">
          <label htmlFor="direction">Direction</label>
          <select id="direction" name="direction" required defaultValue="BOTH">
            <option value="INFLOW">Inflow</option>
            <option value="OUTFLOW">Outflow</option>
            <option value="BOTH">Both</option>
          </select>
        </div>
        <button type="submit" className="btn-primary">
          Add category
        </button>
      </form>

      {categories.length === 0 ? (
        <p className="empty">No categories yet.</p>
      ) : (
        <table className="table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Direction</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {categories.map((c) => (
              <tr key={c.id}>
                <td>{c.name}</td>
                <td>{c.direction}</td>
                <td>
                  <span className={`badge ${c.is_active ? "badge--active" : "badge--inactive"}`}>
                    {c.is_active ? "Active" : "Inactive"}
                  </span>
                </td>
                <td>
                  <div className="row-actions">
                    <form action={toggleCategoryActive}>
                      <input type="hidden" name="id" value={c.id} />
                      <input type="hidden" name="active" value={String(c.is_active)} />
                      <button type="submit" className="btn-ghost btn-sm">
                        {c.is_active ? "Deactivate" : "Activate"}
                      </button>
                    </form>
                    <DeleteButton action={deleteCategory} id={c.id} label={c.name} />
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