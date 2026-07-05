-- Add recurring_template_id to cashflow_transactions so the recurring
-- generation cron job can link generated transactions back to their source
-- template. This column is the secondary idempotency guard: if the job is
-- interrupted between creating a transaction and advancing next_run_date,
-- a subsequent run can detect the duplicate via this link.

ALTER TABLE cashflow_transactions
  ADD COLUMN recurring_template_id UUID NULL
  REFERENCES recurring_transaction_templates(id) ON DELETE SET NULL;

CREATE INDEX idx_cashflow_recurring_template
  ON cashflow_transactions (recurring_template_id)
  WHERE recurring_template_id IS NOT NULL;