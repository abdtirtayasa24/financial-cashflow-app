# Hierarchies are structural only — not used for report rollup

The schema includes self-referencing parent IDs on `departments` and `cashflow_categories`, but for the MVP, report filters and dashboard queries match on the exact department or category only — selecting a parent does not include its children. The hierarchies exist for UI organization (tree display, indented dropdowns) only. This avoids recursive CTEs in reporting queries and keeps the financial model straightforward. Rollup by hierarchy can be added post-MVP if needed, at which point all report queries would need to be updated.

## Considered Options

- **Structural only (chosen)** — report filters match exact department/category. Simple flat queries. No recursive CTEs.
- **Full rollup** — selecting a parent department includes all descendants in reports. Requires recursive CTEs on every report query. More powerful but significantly more complex and slower for deep hierarchies.

## Consequences

- All report APIs (`summary`, `monthly-trend`, `by-category`, `by-department`, `cash-account-balances`) can use simple `WHERE department_id = :id` filters.
- If rollup is needed later, every report query and endpoint must be updated to traverse the hierarchy.
- The `parent_department_id` and `parent_category_id` columns should not be removed — they are used for UI organization and are the foundation for future rollup support.