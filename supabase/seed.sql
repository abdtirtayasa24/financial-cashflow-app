INSERT INTO departments (name, code)
VALUES
  ('Finance', 'FIN'),
  ('Operations', 'OPS'),
  ('Sales', 'SAL'),
  ('Management', 'MGT');

INSERT INTO payment_methods (name)
VALUES
  ('Cash'),
  ('Bank Transfer'),
  ('Debit Card'),
  ('Credit Card'),
  ('E-Wallet');

INSERT INTO cashflow_categories (name, direction)
VALUES
  ('Sales Income', 'INFLOW'),
  ('Other Income', 'INFLOW'),
  ('Vendor Payment', 'OUTFLOW'),
  ('Payroll', 'OUTFLOW'),
  ('Operational Expense', 'OUTFLOW'),
  ('Tax', 'OUTFLOW'),
  ('Loan', 'BOTH');

INSERT INTO cash_accounts (
  name,
  account_type,
  opening_balance,
  opening_balance_date,
  currency
)
VALUES
  ('Main Bank Account', 'BANK', 0, CURRENT_DATE, 'IDR'),
  ('Petty Cash', 'CASH', 0, CURRENT_DATE, 'IDR');
