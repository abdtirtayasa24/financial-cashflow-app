-- Approved cashflow report view.
-- Only APPROVED transactions are included in official dashboards and reports.
-- VOIDED is automatically excluded (status is no longer APPROVED).

CREATE VIEW approved_cashflow AS
SELECT
  t.id,
  t.transaction_no,
  t.transaction_date,
  t.direction,
  t.amount,
  t.base_amount,
  t.cash_account_id,
  ca.name AS cash_account_name,
  t.department_id,
  d.name AS department_name,
  d.code AS department_code,
  t.category_id,
  c.name AS category_name,
  t.payment_method_id,
  pm.name AS payment_method_name,
  t.counterparty_name,
  t.reference_no,
  t.description,
  t.status,
  t.reviewed_at
FROM cashflow_transactions t
JOIN cash_accounts ca ON ca.id = t.cash_account_id
JOIN departments d ON d.id = t.department_id
JOIN cashflow_categories c ON c.id = t.category_id
LEFT JOIN payment_methods pm ON pm.id = t.payment_method_id
WHERE t.status = 'APPROVED';