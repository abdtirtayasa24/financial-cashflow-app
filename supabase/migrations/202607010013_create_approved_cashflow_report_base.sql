-- Approved-only reporting base view for dashboard/report APIs.
-- Reuse the existing approved_cashflow view so the APPROVED-only reporting
-- invariant is defined in one place.

CREATE OR REPLACE VIEW approved_cashflow_report_base AS
SELECT
  id,
  transaction_no,
  transaction_date,
  direction,
  amount,
  -- MVP reports are IDR/base_amount based. The existing approved_cashflow view
  -- predates this report-base alias and does not expose transaction currency.
  'IDR'::CHAR(3) AS currency,
  base_amount,
  cash_account_id,
  cash_account_name,
  department_id,
  department_name,
  department_code,
  category_id,
  category_name,
  payment_method_id,
  payment_method_name,
  counterparty_name,
  reference_no,
  description,
  status,
  reviewed_at
FROM approved_cashflow;
