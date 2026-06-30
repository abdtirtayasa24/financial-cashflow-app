-- app_settings: simple key/value store managed by System Admin.
-- notifications: in-app notifications (MVP, no email).
-- recurring_transaction_templates: prototypes + recurrence schedule for cron generation.

CREATE TABLE app_settings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  key VARCHAR(80) NOT NULL UNIQUE,
  value TEXT NOT NULL,
  updated_by UUID NULL REFERENCES user_profiles(id) ON DELETE SET NULL,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE notifications (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
  type VARCHAR(40) NOT NULL CHECK (
    type IN ('PENDING_APPROVAL', 'RECURRING_DRAFT_READY')
  ),
  title VARCHAR(180) NOT NULL,
  message TEXT NOT NULL,
  related_transaction_id UUID NULL REFERENCES cashflow_transactions(id) ON DELETE CASCADE,
  is_read BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_notifications_user_unread
  ON notifications (user_id, is_read, created_at DESC);

CREATE TABLE recurring_transaction_templates (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  department_id UUID NOT NULL REFERENCES departments(id),
  category_id UUID NOT NULL REFERENCES cashflow_categories(id),
  cash_account_id UUID NOT NULL REFERENCES cash_accounts(id),
  payment_method_id UUID NULL REFERENCES payment_methods(id),
  direction VARCHAR(20) NOT NULL CHECK (direction IN ('INFLOW', 'OUTFLOW')),
  amount NUMERIC(18,2) NOT NULL CHECK (amount > 0),
  currency CHAR(3) NOT NULL DEFAULT 'IDR',
  counterparty_name VARCHAR(180) NULL,
  reference_no VARCHAR(120) NULL,
  description TEXT NULL,
  submission_mode VARCHAR(20) NOT NULL CHECK (submission_mode IN ('AUTO_SUBMIT', 'DRAFT')),
  frequency VARCHAR(10) NOT NULL CHECK (frequency IN ('DAILY', 'WEEKLY', 'MONTHLY')),
  interval INT NOT NULL CHECK (interval >= 1) DEFAULT 1,
  next_run_date DATE NOT NULL,
  end_date DATE NULL,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_by UUID NOT NULL REFERENCES user_profiles(id),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index foreign keys (Postgres does not index FK columns automatically).
CREATE INDEX idx_recurring_department_id ON recurring_transaction_templates (department_id);
CREATE INDEX idx_recurring_category_id ON recurring_transaction_templates (category_id);
CREATE INDEX idx_recurring_cash_account_id ON recurring_transaction_templates (cash_account_id);
CREATE INDEX idx_recurring_payment_method_id ON recurring_transaction_templates (payment_method_id);
CREATE INDEX idx_recurring_created_by ON recurring_transaction_templates (created_by);

-- Used by the generate_recurring_transactions cron job.
CREATE INDEX idx_recurring_due ON recurring_transaction_templates (is_active, next_run_date)
  WHERE is_active = TRUE;