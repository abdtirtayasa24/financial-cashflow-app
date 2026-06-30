---
title: Agent-Guideline

---

## Agent Guideline

### 1. Purpose

This section defines how an AI coding agent should execute this specification safely and consistently.

The agent must treat this document as the source of truth for the MVP implementation of the financial cashflow recording and BI dashboard application.

The goal is to produce production-ready code and infrastructure that can be reviewed, tested, and deployed by human engineers.

---

### 2. Execution Principles

The AI agent must follow these principles:

* Implement the MVP exactly as described in this specification.
* Prefer simple, maintainable solutions over complex abstractions.
* Do not introduce unapproved technologies.
* Do not replace the selected stack.
* Do not use an ORM.
* Do not store uploaded files in Supabase Storage.
* Do not expose Supabase service-role keys to the frontend.
* Do not bypass FastAPI authorization checks.
* Do not include unapproved transaction statuses or accounting models.
* Do not implement full double-entry accounting in the MVP.
* Do not build features listed under “Won’t Have in MVP”.

Selected stack:

```text
Frontend: Next.js
Backend API: FastAPI
Database: Supabase PostgreSQL
Database Access: Supabase client builder + repository pattern
Migrations: Supabase migrations
Charts: Apache ECharts
File Storage: VPS local storage
Jobs: Cron jobs
Deployment: Docker Compose on VPS
```

---

### 3. Required Development Flow

The AI agent must work in small, reviewable increments.

For every feature, follow this order:

```text
1. Read the relevant spec section.
2. Identify the exact files to create or modify.
3. Implement database migration first if schema changes are needed.
4. Implement backend schemas.
5. Implement repository methods.
6. Implement service-layer business rules.
7. Implement FastAPI routes.
8. Implement frontend API client.
9. Implement frontend page or component.
10. Add tests where practical.
11. Verify security and role permissions.
12. Summarize completed work and remaining risks.
```

The agent must not skip directly to frontend implementation before backend contracts are clear.

---

### 4. Repository Rules

The agent must use this repository structure:

```text
financial-cashflow-app/
  apps/
    web/
    api/
  supabase/
    migrations/
    seed.sql
  deploy/
    nginx/
    docker-compose.yml
    .env.example
  scripts/
  docs/
```

The agent must not place backend business logic inside frontend code.

The agent must not place raw Supabase calls directly inside FastAPI routers.

Correct backend dependency flow:

```text
router.py
  -> service.py
    -> repository.py
      -> Supabase client builder
```

---

### 5. Backend Coding Guidelines

FastAPI modules must follow this structure:

```text
modules/
  transactions/
    router.py
    schemas.py
    service.py
    repository.py
```

Backend rules:

* `router.py` handles HTTP concerns only.
* `schemas.py` contains Pydantic request and response models.
* `service.py` contains business rules.
* `repository.py` contains Supabase database access.
* `core/auth.py` validates the current user.
* `core/supabase_client.py` creates the Supabase client.
* `core/config.py` reads environment variables.

The agent must keep financial rules in the service layer, not in route handlers.

---

### 6. Database and Migration Rules

The agent must use Supabase SQL migrations for schema changes.

Migration files must be placed in:

```text
supabase/migrations/
```

The agent must create migrations in chronological order using descriptive names, for example:

```text
202607010001_create_departments.sql
202607010002_create_user_profiles.sql
202607010003_create_cash_accounts.sql
```

Database rules:

* Use `UUID` primary keys with `gen_random_uuid()`.
* Use `TIMESTAMPTZ` for timestamps.
* Use `NUMERIC(18,2)` for money values.
* Use `CHECK` constraints for enums.
* Use indexes for report filters.
* Use `user_profiles` linked to `auth.users`.
* Do not create a standalone `users` table.

The agent must preserve this reporting rule:

```sql
WHERE status = 'APPROVED'
```

Only approved transactions are included in official dashboards and reports.

---

### 7. Authentication and Authorization Rules

The agent must use Supabase Auth for identity.

FastAPI must validate the current user before allowing access to protected APIs.

Role permissions:

| Role               | Allowed                                                                                 |
| ------------------ | --------------------------------------------------------------------------------------- |
| Employee           | Create, edit own draft/rejected transactions, submit own transactions, view own records |
| Department Manager | View own department transactions                                                        |
| Finance Admin      | View all records, approve, reject, void, export reports                                 |
| Management         | View dashboard and reports only                                                         |
| System Admin       | Manage users, departments, categories, payment methods, and cash accounts               |

The agent must enforce authorization in the backend even if frontend routes are hidden.

The frontend permission checks are for user experience only. They are not sufficient for security.

---

### 8. Transaction Workflow Rules

The agent must implement exactly this transaction lifecycle:

```text
DRAFT
  -> SUBMITTED
    -> APPROVED
    -> REJECTED
REJECTED
  -> DRAFT
APPROVED
  -> VOIDED
```

Rules:

* New transactions start as `DRAFT`.
* Only `DRAFT` or `REJECTED` transactions can be submitted.
* Only `SUBMITTED` transactions can be approved.
* Only `SUBMITTED` transactions can be rejected.
* Only `APPROVED` transactions can be voided.
* Approved transactions cannot be edited directly.
* Voiding requires a reason.
* Rejection requires a reason.
* All status changes must create audit logs.

The agent must not implement direct editing of approved transactions.

---

### 9. File Upload Rules

The agent must store uploaded files on VPS local storage.

Upload path format:

```text
/var/app/financial-cashflow/uploads/
  transactions/
    YYYY/
      MM/
        <transaction_id>/
          <uuid>.<extension>
```

Rules:

* Do not expose upload folders through Nginx.
* Do not store files in Supabase Storage.
* Store only metadata in Supabase PostgreSQL.
* Download files only through FastAPI.
* Validate user permission before streaming a file.
* Rename uploaded files to UUID-based filenames.
* Preserve the original filename in database metadata.
* Allow only PDF, PNG, JPG, and JPEG.
* Enforce maximum file size of 10 MB.

---

### 10. Reporting and Dashboard Rules

The agent must implement reporting APIs before dashboard charts.

Required report APIs:

```text
GET /api/reports/summary
GET /api/reports/monthly-trend
GET /api/reports/by-category
GET /api/reports/by-department
GET /api/reports/cash-account-balances
GET /api/reports/pending-approvals
POST /api/reports/export
```

Dashboard must include:

* Total inflow.
* Total outflow.
* Net cashflow.
* Current cash balance.
* Monthly cashflow trend.
* Category breakdown.
* Department breakdown.
* Cash account balance.
* Pending approval count.

Rules:

* Reports must exclude `DRAFT`, `SUBMITTED`, `REJECTED`, and `VOIDED`.
* Reports must include only `APPROVED`.
* Dashboard filters must include date range.
* Dashboard should support department and cash account filters.
* Apache ECharts must be used for charts.

---

### 11. Cron Job Rules

Cron jobs must be idempotent.

Required jobs:

```text
refresh_report_snapshots.py
cleanup_old_exports.py
check_missing_attachments.py
monthly_financial_snapshot.py
backup_uploads.sh
```

Rules:

* Running the same job twice must not duplicate financial data.
* Failed jobs must log errors.
* Jobs must not alter approved transaction values.
* Jobs may create report snapshots.
* Jobs may delete expired exports.
* Jobs may flag missing attachments.
* Jobs may back up uploaded files.

---

### 12. Frontend Guidelines

The frontend must use Next.js and communicate with FastAPI for business APIs.

Frontend rules:

* Do not call Supabase database APIs directly from UI components.
* Use Supabase frontend client only for login/session handling when needed.
* Use FastAPI for transactions, approvals, files, reports, and admin operations.
* Keep API calls in a shared API client module.
* Keep dashboard chart components reusable.
* Ensure pages are responsive for desktop and mobile browser.
* Hide unauthorized menu items, but still rely on backend authorization.

Required pages:

```text
/login
/dashboard
/transactions
/transactions/new
/transactions/[id]
/approvals
/reports
/admin/users
/admin/departments
/admin/categories
/admin/cash-accounts
```

---

### 13. Testing Requirements

The agent should add tests for critical backend logic.

Minimum backend tests:

```text
- Invalid token is rejected.
- Inactive user is rejected.
- Employee cannot view other users’ transactions.
- Employee cannot approve transactions.
- Finance Admin can approve submitted transactions.
- Approved transactions cannot be edited.
- Rejected transactions require a reason.
- Voided transactions require a reason.
- Reports include only approved transactions.
- File download requires permission.
```

Minimum frontend checks:

```text
- Login page renders.
- Dashboard page loads.
- Transaction creation form validates required fields.
- Approval page is restricted to Finance Admin.
- Attachment upload rejects invalid file types.
```

---

### 14. Environment and Secret Handling

The agent must create `.env.example` files but must not commit real secrets.

Allowed public frontend variables:

```text
NEXT_PUBLIC_API_BASE_URL
NEXT_PUBLIC_SUPABASE_URL
NEXT_PUBLIC_SUPABASE_ANON_KEY
```

Backend-only secrets:

```text
SUPABASE_SERVICE_ROLE_KEY
SUPABASE_URL
UPLOAD_DIR
JWT_SECRET_OR_JWKS_CONFIG
```

Rules:

* Never place service-role keys in frontend files.
* Never hardcode credentials.
* Never print secrets in logs.
* Never commit `.env` files.
* Use `.env.example` with placeholder values only.

---

### 15. Deployment Rules

The agent must support Docker Compose deployment on a VPS.

Required services:

```text
web
api
nginx
```

Required persistent volumes:

```text
uploads_data
exports_data
```

Deployment must include:

* Dockerfile for Next.js app.
* Dockerfile for FastAPI app.
* Docker Compose file.
* Nginx config.
* Upload volume mount.
* Environment variable example.
* Backup script for uploads.

Nginx must route:

```text
/api/*  -> FastAPI
/*      -> Next.js
```

Nginx must not directly serve the upload directory.

---

### 16. Prohibited Agent Actions

The AI agent must not:

* Add full accounting journal entries.
* Add double-entry ledger functionality.
* Add payroll processing.
* Add automated tax filing.
* Add real-time bank synchronization.
* Add external BI tools.
* Replace FastAPI with another backend framework.
* Replace Supabase PostgreSQL with another database.
* Add Prisma, SQLAlchemy, Django ORM, or another ORM.
* Store receipts in the database as binary data.
* Make uploaded files publicly accessible.
* Expose service-role keys to the frontend.
* Disable audit logging.
* Include non-approved transactions in official reports.

---

### 17. Completion Definition

A task is complete only when:

```text
1. Code follows the selected architecture.
2. Backend authorization is enforced.
3. Database changes are handled through Supabase migrations.
4. Financial business rules are implemented in service layer.
5. Transaction actions create audit logs.
6. Reports include only approved transactions.
7. File uploads are stored securely on VPS local storage.
8. Docker Compose can run the affected services.
9. Tests or verification steps are provided.
10. Remaining risks or TODOs are documented.
```

---

### 18. Agent Output Format

After each implementation task, the AI agent should respond with:

```text
Summary:
- What was implemented.

Files changed:
- List of files created or modified.

Database changes:
- Migration files added or changed.

How to test:
- Commands or manual steps to verify.

Security notes:
- Permissions, secrets, or access-control considerations.

Remaining TODOs:
- Any incomplete or deferred items.
```

The agent must be explicit about incomplete work and must not claim production readiness unless the deployment, security, and testing criteria are satisfied.
