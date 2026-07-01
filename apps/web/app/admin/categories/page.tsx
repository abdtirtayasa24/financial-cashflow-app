import {
  createCategory,
  deleteCategory,
  toggleCategoryActive,
} from "@/app/actions";
import { DeleteButton } from "@/components/DeleteButton";
import { apiGet } from "@/lib/api";
import type { Category } from "@/lib/types";

const DIRECTION_LABELS: Record<string, string> = {
  INFLOW: "Inflow",
  OUTFLOW: "Outflow",
  BOTH: "Both",
};

export default async function CategoriesPage() {
  const categories = await apiGet<Category[]>("/api/categories");

  return (
    <div className="container">
      <div className="page-header">
        <div>
          <h1>Cashflow Categories</h1>
          <p className="page-header__subtitle">Classify transactions by income and expense categories.</p>
        </div>
      </div>

      <div className="section">
        <form action={createCategory} className="card form-grid" aria-label="Create category">
          <div className="form-row">
            <div className="field">
              <label htmlFor="name">Name</label>
              <input id="name" name="name" required placeholder="Sales Income" />
            </div>
            <div className="field">
              <label htmlFor="direction">Direction</label>
              <select id="direction" name="direction" required defaultValue="BOTH">
                <option value="INFLOW">Inflow</option>
                <option value="OUTFLOW">Outflow</option>
                <option value="BOTH">Both</option>
              </select>
            </div>
          </div>
          <div className="form-actions">
            <button type="submit" className="btn-primary">
              Add category
            </button>
          </div>
        </form>
      </div>

      <div className="section">
        <h2 className="section__title">All categories</h2>
        {categories.length === 0 ? (
          <div className="empty">
            <div className="empty__icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z" />
                <line x1="7" y1="7" x2="7.01" y2="7" />
              </svg>
            </div>
            <div className="empty__title">No categories yet</div>
            <p className="empty__desc">Create categories to classify cash inflows and outflows.</p>
          </div>
        ) : (
          <div className="table-wrap">
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
                    <td style={{ fontWeight: 500 }}>{c.name}</td>
                    <td className="text-secondary">{DIRECTION_LABELS[c.direction] ?? c.direction}</td>
                    <td>
                      <span className={`badge ${c.is_active ? "badge--active" : "badge--inactive"}`}>
                        <span className="badge__dot" aria-hidden="true" />
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
          </div>
        )}
      </div>
    </div>
  );
}