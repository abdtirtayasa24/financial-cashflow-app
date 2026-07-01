# Financial Cashflow Recording & BI Reporting

A centralized application for recording, classifying, reviewing, and analyzing cash inflows and outflows across a single company with multiple departments. Built as an MVP with a clear scope boundary.

## MVP Scope Boundary

The MVP includes features from both the **Must Have** and **Should Have** tiers of the spec. **Could Have** features (multi-currency, bank reconciliation, forecasting, accounting/bank integrations, tax reporting) are explicitly deferred until after the MVP is fully implemented.

### In scope (Must Have + Should Have)

- Cash inflow / outflow recording with required fields
- Supporting document attachments (VPS local storage)
- Financial categories (including custom)
- Role-based access control (5 roles)
- Finance admin review / approve / reject / void workflow
- Audit trail
- BI dashboard with filters (date, category, department, payment method, status)
- Financial reports (cashflow, income vs expense, category breakdown)
- Multi-department / cost-center tracking
- Recurring transactions
- Report export to Excel and PDF
- Dashboard charts (monthly trend, top expense categories, cash balance movement)
- Notifications for pending approvals
- CSV / Excel transaction import

### Recurring Transactions

A **Recurring Transaction Template** stores a transaction prototype plus a recurrence schedule and a submission mode.

**Two submission modes:**

- **Auto-submit** (`AUTO_SUBMIT`): When the scheduled date arrives, the system creates the transaction *and* submits it automatically. It lands in `SUBMITTED` status, awaiting Finance Admin approval. Approval is never bypassed.
- **Draft/Reminder** (`DRAFT`): The system creates a `DRAFT` transaction on the scheduled date. The user must review and submit it manually through the normal workflow.

**Recurrence config:** frequency (DAILY/WEEKLY/MONTHLY), interval (every N periods), next_run_date, optional end_date, is_active flag.

**Generation mechanism:** A cron job checks `next_run_date <= today` and generates a transaction from each due template, then advances `next_run_date` by the configured interval.

**Authorization for template creation:**
- **Finance Admin** — can create auto-submit or draft/reminder templates for any department.
- **Employee** — can create draft/reminder templates only for their own department. Cannot create auto-submit templates.
- **Department Manager** — can view recurring templates for their department but cannot create them.

**Normal workflow applies:** All generated transactions follow DRAFT → SUBMITTED → APPROVED (or REJECTED). Auto-submit just skips the manual creation+submission step, not the approval gate.

### In-App Notifications

Notifications are **in-app only** for the MVP — no email or external messaging service. Finance Admins are active users and will see notifications when logged in.

**Design:**
- A `notifications` table: `id`, `user_id`, `type` (e.g. `PENDING_APPROVAL`, `RECURRING_DRAFT_READY`), `title`, `message`, `related_transaction_id`, `is_read`, `created_at`.
- When a transaction is submitted, the service layer inserts a notification for all active Finance Admin users.
- When a recurring draft is generated, the service layer inserts a notification for the template creator.
- Frontend fetches notifications on page load, shows unread count in a bell icon.
- Email notifications can be added post-MVP without architectural changes.

### Transaction Import (CSV/Excel)

**Finance Admin only.** Importing bulk transactions is a sensitive operation. Employees cannot import.

**Design:**
- Imported transactions start as `DRAFT` — each row must be reviewed and submitted through the normal workflow. No auto-submit on import.
- **Expected columns:** `transaction_date`, `direction`, `amount`, `category_name`, `department_code`, `cash_account_name`, `payment_method_name`, `counterparty_name`, `reference_no`, `description`.
- Category, department, cash account, and payment method are matched by name/code — the import resolves them to IDs.
- **Partial success:** Import valid rows, collect errors for invalid rows, return a summary report (e.g. "42 of 50 rows imported, 8 errors: row 3 — unknown category 'Foo', row 7 — amount must be positive").
- **Row limit: 500 rows per file** for MVP. Larger imports can be split.

### Row Level Security (RLS)

RLS is enabled on all tables as a defense-in-depth layer, even though the backend uses the service role key (which bypasses RLS).

- **`user_profiles`**: users can only read their own profile (`WHERE auth.uid() = id`). This is the one table the frontend may access via Supabase client for session info.
- **All other tables**: no RLS policy = no access via anon key. All data access goes through FastAPI using the service role key.
- Even if the anon key is compromised, an attacker can only read their own profile — no access to transactions, financial data, or admin tables.

### updated_at Handling

PostgreSQL triggers maintain `updated_at` automatically on all tables that have the column. A single `set_updated_at()` function + `BEFORE UPDATE` triggers per table. This ensures `updated_at` is always correct regardless of how the update happens (app, cron, or manual SQL).

- Payment method is **required by the application** (service layer validation) for manual transaction entry, but the database column remains `NULL`-able as a safety valve for edge cases (CSV import with missing column, adjusting entries). The user must fill it in during draft review before submission.

### Department & Category Hierarchies

Hierarchies (`parent_department_id`, `parent_category_id`) are **structural/organizational only** for the MVP — not used for report rollup.

- Transactions are assigned to exactly one department and one category.
- Dashboard and report filters match on the **exact department or category** — selecting a parent does NOT include its children.
- The parent-child relationships exist for **UI organization** (tree display, indented dropdowns), not aggregation.
- Recursive rollup by hierarchy can be added post-MVP if needed.

### Editable Fields

All transaction fields are editable while in **DRAFT** or **REJECTED** status:

`transaction_date`, `direction`, `amount`, `cash_account_id`, `department_id`, `category_id`, `payment_method_id`, `counterparty_name`, `reference_no`, `description`

**Not editable** (system-managed):
`transaction_no`, `created_by`, `created_at`, `updated_at`, `status`, `submitted_at`, `reviewed_by`, `reviewed_at`, `rejection_reason`, `void_reason`

Editing creates an audit log entry capturing old and new values.

### Transaction Deletion Policy

- **DRAFT and REJECTED transactions** can be **hard-deleted** by the creator or Finance Admin. These have never been submitted and have no financial impact.
- **SUBMITTED, APPROVED, and VOIDED transactions cannot be deleted** — they have audit trail significance.
- Deleting a DRAFT/REJECTED transaction also deletes its attachments (metadata + VPS files) and its audit logs.
- A delete action creates a final audit log entry before the deletion happens.

### Roles & Authorization

Roles are **strictly one-per-user** — no dual roles, no overlapping permissions.

| Role | Permissions |
|------|-------------|
| **Employee** | Create draft transactions for own department, edit own draft/rejected transactions, submit own transactions, view own transactions |
| **Department Manager** | View all transactions for own department. **Cannot** create, edit, submit, approve, reject, or void transactions |
| **Finance Admin** | View all transactions across all departments, create transactions for any department, approve, reject, void, export reports |
| **Management** | View dashboard and reports only. **Cannot** create, edit, approve, reject, or void transactions |
| **System Admin** | Manage users, departments, categories, payment methods, cash accounts, and app settings. Can view all transactions read-only. **Cannot** create, edit, submit, delete, approve, reject, or void transactions |

If a department head needs to create transactions, they should be assigned the `EMPLOYEE` role, not `DEPARTMENT_MANAGER`.

> **System Admin transaction access:** System Admin is granted read-only access to transactions (list and detail) so the role is not 403-blocked when browsing the application and can support troubleshooting. It can never create, edit, submit, delete, approve, reject, or void transactions — those are enforced in the backend service layer.

### App Settings & Attachment Threshold

A simple `app_settings` table stores configurable values: `key VARCHAR`, `value TEXT`, `updated_by UUID`, `updated_at TIMESTAMPTZ`. Managed by System Admin through the admin UI — no redeploy needed to change values.

**Attachment threshold settings:**

- `attachment_threshold_enabled` (boolean, default `true`) — master switch. When `false`, attachments are always optional regardless of amount. When `true`, attachments are required for transactions with `amount >= attachment_threshold_amount`.
- `attachment_threshold_amount` (numeric, default `5,000,000` IDR) — the threshold amount in IDR.

The rule is enforced at submission time (DRAFT/REJECTED → SUBMITTED). If enabled and `amount >= threshold` and no attachments exist, submission is rejected with a message like "Attachments are required for transactions of 5,000,000 IDR or above."

### Cash Balance Calculation

For each cash account:

```
current_balance = opening_balance
  + SUM(base_amount WHERE direction = 'INFLOW' AND status = 'APPROVED' AND transaction_date >= opening_balance_date)
  - SUM(base_amount WHERE direction = 'OUTFLOW' AND status = 'APPROVED' AND transaction_date >= opening_balance_date)
```

Key rules:
- Only **APPROVED** transactions count toward the balance.
- **VOIDED** transactions are excluded (status is no longer APPROVED, so the effect is automatically reversed).
- Only transactions on or after `opening_balance_date` are summed.
- Dashboard shows **total across all active cash accounts**.
- `cash-account-balances` endpoint shows per-account breakdown.
- **Current cash balance is always as-of now** — not affected by the dashboard's date range filter. It represents actual money available. The inflow/outflow/net KPIs *are* scoped to the date range filter.

### Transaction Number Format

Format: `{DIRECTION}-{YYYYMM}-{SEQ:06d}`

Examples: `INFLOW-202607-000001`, `OUTFLOW-202607-000001`

- `DIRECTION` is `INFLOW` or `OUTFLOW`
- `YYYYMM` is the year + month of the transaction date
- `SEQ` is a zero-padded sequence number, scoped per direction + year-month (resets each month)
- Generated by querying `MAX(seq) + 1` within the same direction + year-month partition, with a unique constraint to handle race conditions

### Transaction Lifecycle

The transaction state machine:

```
DRAFT ──────► SUBMITTED ──────► APPROVED ──────► VOIDED
                  │                  │
                  └────► REJECTED ◄──┘ (reject only from SUBMITTED)
                  │
REJECTED ─────────► SUBMITTED  (direct resubmit after editing — no DRAFT intermediate step)
```

- New transactions start as `DRAFT`.
- `DRAFT` and `REJECTED` are both valid pre-submission states. A rejected transaction can be edited and resubmitted directly to `SUBMITTED` — no need to pass through `DRAFT` first.
- Only `SUBMITTED` transactions can be approved or rejected.
- Only `APPROVED` transactions can be voided.
- Approved transactions cannot be edited.
- Voiding and rejection both require a reason.
- All status changes create audit logs.

### Deferred (Could Have — post-MVP)

- Multi-currency support (schema fields exist but are future-proofing only)
- Bank statement upload and reconciliation
- Budget vs actual reporting
- Forecasting based on historical cashflow
- Integration with accounting systems
- Integration with bank APIs
- Tax reporting support

### Milestone Plan

The original spec defined 8 milestones. Three "Should Have" features (recurring transactions, in-app notifications, CSV/Excel import) and app settings management had no milestone home. The updated plan uses clean sequential numbering 1–10:

| # | Milestone | Key Deliverables |
|---|----------|-----------------|
| 1 | Project Foundation | Monorepo, Next.js + FastAPI init, Docker Compose, Nginx, Supabase project, env structure |
| 2 | Database and Authentication | All migrations (including `app_settings`, `notifications`, `recurring_transaction_templates`), Supabase Auth login, JWT validation, RBAC, admin user creation flow |
| 3 | Cashflow Transaction Management | Transaction CRUD, list, detail, filters, draft creation, submission, attachment upload/download, audit logging |
| 4 | Finance Approval Workflow | Approval queue, approve/reject/void actions, permission checks, rejection/void reasons |
| 5 | Notifications | Notifications table, notification service (triggered on submit + recurring draft generation), notification API endpoints, bell icon in frontend |
| 6 | Reporting APIs | Approved cashflow SQL view, summary/monthly-trend/by-category/by-department/cash-account-balances/pending-approvals APIs, Excel/PDF export |
| 7 | BI Dashboard | Dashboard page, date range + department + cash account filters, KPI cards, Apache ECharts charts, pending approval indicator |
| 8 | Cron Jobs and Operational Scripts | Daily snapshot, monthly snapshot, export cleanup, missing attachment check, upload backup, cron config |
| 9 | Recurring Transactions & CSV/Excel Import | Recurring template CRUD, generation cron job, CSV/Excel import endpoint + UI, app settings admin UI |
| 10 | Production Deployment and UAT | Production VPS, Docker Compose deployment, HTTPS, migrations applied, seed data, UAT, bug fixes |