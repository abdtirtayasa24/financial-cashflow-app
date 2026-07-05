-- Demo data for local/manual QA only.
--
-- Run after Supabase migrations, for example:
--   psql "$SUPABASE_DB_URL" -f supabase/seed_demo_data.sql
-- or paste/execute this file in a local/staging database with service-role privileges.
--
-- Demo login accounts all use password: DemoPassword123!
--   finance.admin@example.test      FINANCE_ADMIN
--   management@example.test         MANAGEMENT
--   sysadmin@example.test           SYSTEM_ADMIN
--   ops.employee@example.test       EMPLOYEE
--   sales.employee@example.test     EMPLOYEE
--   ops.manager@example.test        DEPARTMENT_MANAGER
--
-- This file intentionally uses reserved .test email addresses and deterministic
-- UUIDs so it is safe to rerun in non-production environments.

BEGIN;

CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA extensions;

-- ── Auth users for local QA login ─────────────────────────────
INSERT INTO auth.users (
  id,
  instance_id,
  aud,
  role,
  email,
  encrypted_password,
  email_confirmed_at,
  created_at,
  updated_at,
  raw_app_meta_data,
  raw_user_meta_data,
  is_super_admin,
  confirmation_token,
  email_change,
  email_change_token_new,
  recovery_token
)
VALUES
  (
    '00000000-0000-0000-0000-000000000101',
    '00000000-0000-0000-0000-000000000000',
    'authenticated',
    'authenticated',
    'finance.admin@example.test',
    crypt('DemoPassword123!', gen_salt('bf')),
    now(),
    now(),
    now(),
    '{"provider":"email","providers":["email"]}'::jsonb,
    '{"full_name":"Rina Santoso"}'::jsonb,
    false,
    '',
    '',
    '',
    ''
  ),
  (
    '00000000-0000-0000-0000-000000000102',
    '00000000-0000-0000-0000-000000000000',
    'authenticated',
    'authenticated',
    'management@example.test',
    crypt('DemoPassword123!', gen_salt('bf')),
    now(),
    now(),
    now(),
    '{"provider":"email","providers":["email"]}'::jsonb,
    '{"full_name":"Budi Hartono"}'::jsonb,
    false,
    '',
    '',
    '',
    ''
  ),
  (
    '00000000-0000-0000-0000-000000000103',
    '00000000-0000-0000-0000-000000000000',
    'authenticated',
    'authenticated',
    'sysadmin@example.test',
    crypt('DemoPassword123!', gen_salt('bf')),
    now(),
    now(),
    now(),
    '{"provider":"email","providers":["email"]}'::jsonb,
    '{"full_name":"Sari Wijaya"}'::jsonb,
    false,
    '',
    '',
    '',
    ''
  ),
  (
    '00000000-0000-0000-0000-000000000104',
    '00000000-0000-0000-0000-000000000000',
    'authenticated',
    'authenticated',
    'ops.employee@example.test',
    crypt('DemoPassword123!', gen_salt('bf')),
    now(),
    now(),
    now(),
    '{"provider":"email","providers":["email"]}'::jsonb,
    '{"full_name":"Andi Pratama"}'::jsonb,
    false,
    '',
    '',
    '',
    ''
  ),
  (
    '00000000-0000-0000-0000-000000000105',
    '00000000-0000-0000-0000-000000000000',
    'authenticated',
    'authenticated',
    'sales.employee@example.test',
    crypt('DemoPassword123!', gen_salt('bf')),
    now(),
    now(),
    now(),
    '{"provider":"email","providers":["email"]}'::jsonb,
    '{"full_name":"Maya Putri"}'::jsonb,
    false,
    '',
    '',
    '',
    ''
  ),
  (
    '00000000-0000-0000-0000-000000000106',
    '00000000-0000-0000-0000-000000000000',
    'authenticated',
    'authenticated',
    'ops.manager@example.test',
    crypt('DemoPassword123!', gen_salt('bf')),
    now(),
    now(),
    now(),
    '{"provider":"email","providers":["email"]}'::jsonb,
    '{"full_name":"Dewi Lestari"}'::jsonb,
    false,
    '',
    '',
    '',
    ''
  )
ON CONFLICT (id) DO UPDATE SET
  email = EXCLUDED.email,
  encrypted_password = EXCLUDED.encrypted_password,
  email_confirmed_at = EXCLUDED.email_confirmed_at,
  updated_at = now(),
  raw_app_meta_data = EXCLUDED.raw_app_meta_data,
  raw_user_meta_data = EXCLUDED.raw_user_meta_data;

INSERT INTO auth.identities (
  id,
  user_id,
  provider_id,
  identity_data,
  provider,
  last_sign_in_at,
  created_at,
  updated_at
)
SELECT
  id,
  id,
  email,
  jsonb_build_object('sub', id::text, 'email', email),
  'email',
  now(),
  now(),
  now()
FROM auth.users
WHERE id IN (
  '00000000-0000-0000-0000-000000000101',
  '00000000-0000-0000-0000-000000000102',
  '00000000-0000-0000-0000-000000000103',
  '00000000-0000-0000-0000-000000000104',
  '00000000-0000-0000-0000-000000000105',
  '00000000-0000-0000-0000-000000000106'
)
ON CONFLICT (provider_id, provider) DO UPDATE SET
  user_id = EXCLUDED.user_id,
  identity_data = EXCLUDED.identity_data,
  updated_at = now();

-- ── Reference data ────────────────────────────────────────────
INSERT INTO departments (name, code, is_active)
VALUES
  ('Finance', 'FIN', true),
  ('Operations', 'OPS', true),
  ('Sales', 'SAL', true),
  ('Management', 'MGT', true),
  ('Information Technology', 'IT', true)
ON CONFLICT (code) DO UPDATE SET
  name = EXCLUDED.name,
  is_active = EXCLUDED.is_active;

INSERT INTO payment_methods (name, is_active)
VALUES
  ('Cash', true),
  ('Bank Transfer', true),
  ('Debit Card', true),
  ('Credit Card', true),
  ('Corporate Card', true),
  ('E-Wallet', true),
  ('QRIS', true)
ON CONFLICT (name) DO UPDATE SET
  is_active = EXCLUDED.is_active;

INSERT INTO cashflow_categories (name, direction, is_active)
VALUES
  ('Product Sales', 'INFLOW', true),
  ('Service Revenue', 'INFLOW', true),
  ('Interest Income', 'INFLOW', true),
  ('Vendor Payments', 'OUTFLOW', true),
  ('Payroll', 'OUTFLOW', true),
  ('Rent and Utilities', 'OUTFLOW', true),
  ('Marketing Expense', 'OUTFLOW', true),
  ('Travel and Entertainment', 'OUTFLOW', true),
  ('Office Supplies', 'OUTFLOW', true),
  ('Tax', 'OUTFLOW', true),
  ('Loan', 'BOTH', true)
ON CONFLICT (name, direction) DO UPDATE SET
  is_active = EXCLUDED.is_active;

INSERT INTO cash_accounts (
  id,
  name,
  account_type,
  opening_balance,
  opening_balance_date,
  currency,
  is_active
)
VALUES
  ('00000000-0000-0000-0000-000000000201', 'BCA Operating Account', 'BANK', 250000000.00, DATE '2026-01-01', 'IDR', true),
  ('00000000-0000-0000-0000-000000000202', 'Mandiri Payroll Account', 'BANK', 75000000.00, DATE '2026-01-01', 'IDR', true),
  ('00000000-0000-0000-0000-000000000203', 'Petty Cash Jakarta', 'CASH', 10000000.00, DATE '2026-01-01', 'IDR', true),
  ('00000000-0000-0000-0000-000000000204', 'GoPay Merchant Wallet', 'EWALLET', 5000000.00, DATE '2026-01-01', 'IDR', true)
ON CONFLICT (id) DO UPDATE SET
  name = EXCLUDED.name,
  account_type = EXCLUDED.account_type,
  opening_balance = EXCLUDED.opening_balance,
  opening_balance_date = EXCLUDED.opening_balance_date,
  currency = EXCLUDED.currency,
  is_active = EXCLUDED.is_active;

INSERT INTO user_profiles (id, department_id, full_name, role, status)
VALUES
  ('00000000-0000-0000-0000-000000000101', (SELECT id FROM departments WHERE code = 'FIN'), 'Rina Santoso', 'FINANCE_ADMIN', 'ACTIVE'),
  ('00000000-0000-0000-0000-000000000102', (SELECT id FROM departments WHERE code = 'MGT'), 'Budi Hartono', 'MANAGEMENT', 'ACTIVE'),
  ('00000000-0000-0000-0000-000000000103', NULL, 'Sari Wijaya', 'SYSTEM_ADMIN', 'ACTIVE'),
  ('00000000-0000-0000-0000-000000000104', (SELECT id FROM departments WHERE code = 'OPS'), 'Andi Pratama', 'EMPLOYEE', 'ACTIVE'),
  ('00000000-0000-0000-0000-000000000105', (SELECT id FROM departments WHERE code = 'SAL'), 'Maya Putri', 'EMPLOYEE', 'ACTIVE'),
  ('00000000-0000-0000-0000-000000000106', (SELECT id FROM departments WHERE code = 'OPS'), 'Dewi Lestari', 'DEPARTMENT_MANAGER', 'ACTIVE')
ON CONFLICT (id) DO UPDATE SET
  department_id = EXCLUDED.department_id,
  full_name = EXCLUDED.full_name,
  role = EXCLUDED.role,
  status = EXCLUDED.status,
  updated_at = now();

INSERT INTO app_settings (key, value, updated_by)
VALUES
  ('attachment_threshold_enabled', 'true', '00000000-0000-0000-0000-000000000103'),
  ('attachment_threshold_amount', '5000000', '00000000-0000-0000-0000-000000000103')
ON CONFLICT (key) DO UPDATE SET
  value = EXCLUDED.value,
  updated_by = EXCLUDED.updated_by,
  updated_at = now();

-- ── Cashflow transactions for dashboard/reporting QA ─────────
INSERT INTO cashflow_transactions (
  id,
  transaction_no,
  transaction_date,
  direction,
  amount,
  currency,
  exchange_rate,
  base_amount,
  cash_account_id,
  department_id,
  category_id,
  payment_method_id,
  counterparty_name,
  reference_no,
  description,
  status,
  created_by,
  submitted_at,
  reviewed_by,
  reviewed_at,
  rejection_reason,
  void_reason,
  created_at,
  updated_at
)
VALUES
  ('00000000-0000-0000-0000-000000000301', 'INFLOW-202601-900001', DATE '2026-01-15', 'INFLOW', 128500000.00, 'IDR', 1, 128500000.00, '00000000-0000-0000-0000-000000000201', (SELECT id FROM departments WHERE code = 'SAL'), (SELECT id FROM cashflow_categories WHERE name = 'Product Sales' AND direction = 'INFLOW'), (SELECT id FROM payment_methods WHERE name = 'Bank Transfer'), 'PT Nusantara Retail', 'INV-2026-001', 'January wholesale product sales collection.', 'APPROVED', '00000000-0000-0000-0000-000000000105', TIMESTAMPTZ '2026-01-15 10:15:00+07', '00000000-0000-0000-0000-000000000101', TIMESTAMPTZ '2026-01-15 15:30:00+07', NULL, NULL, TIMESTAMPTZ '2026-01-15 09:55:00+07', TIMESTAMPTZ '2026-01-15 15:30:00+07'),
  ('00000000-0000-0000-0000-000000000302', 'OUTFLOW-202601-900001', DATE '2026-01-28', 'OUTFLOW', 58000000.00, 'IDR', 1, 58000000.00, '00000000-0000-0000-0000-000000000202', (SELECT id FROM departments WHERE code = 'FIN'), (SELECT id FROM cashflow_categories WHERE name = 'Payroll' AND direction = 'OUTFLOW'), (SELECT id FROM payment_methods WHERE name = 'Bank Transfer'), 'January Payroll Batch', 'PAY-2026-001', 'January employee payroll.', 'APPROVED', '00000000-0000-0000-0000-000000000101', TIMESTAMPTZ '2026-01-27 16:00:00+07', '00000000-0000-0000-0000-000000000101', TIMESTAMPTZ '2026-01-28 09:00:00+07', NULL, NULL, TIMESTAMPTZ '2026-01-27 15:45:00+07', TIMESTAMPTZ '2026-01-28 09:00:00+07'),
  ('00000000-0000-0000-0000-000000000303', 'INFLOW-202602-900001', DATE '2026-02-10', 'INFLOW', 144200000.00, 'IDR', 1, 144200000.00, '00000000-0000-0000-0000-000000000201', (SELECT id FROM departments WHERE code = 'SAL'), (SELECT id FROM cashflow_categories WHERE name = 'Service Revenue' AND direction = 'INFLOW'), (SELECT id FROM payment_methods WHERE name = 'Bank Transfer'), 'PT Sinar Digital', 'INV-2026-018', 'Implementation service milestone payment.', 'APPROVED', '00000000-0000-0000-0000-000000000105', TIMESTAMPTZ '2026-02-10 11:10:00+07', '00000000-0000-0000-0000-000000000101', TIMESTAMPTZ '2026-02-10 14:25:00+07', NULL, NULL, TIMESTAMPTZ '2026-02-10 10:45:00+07', TIMESTAMPTZ '2026-02-10 14:25:00+07'),
  ('00000000-0000-0000-0000-000000000304', 'OUTFLOW-202602-900001', DATE '2026-02-18', 'OUTFLOW', 32750000.00, 'IDR', 1, 32750000.00, '00000000-0000-0000-0000-000000000201', (SELECT id FROM departments WHERE code = 'OPS'), (SELECT id FROM cashflow_categories WHERE name = 'Vendor Payments' AND direction = 'OUTFLOW'), (SELECT id FROM payment_methods WHERE name = 'Bank Transfer'), 'PT Logistik Prima', 'BILL-OPS-020', 'Warehouse and delivery vendor invoice.', 'APPROVED', '00000000-0000-0000-0000-000000000104', TIMESTAMPTZ '2026-02-17 13:40:00+07', '00000000-0000-0000-0000-000000000101', TIMESTAMPTZ '2026-02-18 09:20:00+07', NULL, NULL, TIMESTAMPTZ '2026-02-17 13:10:00+07', TIMESTAMPTZ '2026-02-18 09:20:00+07'),
  ('00000000-0000-0000-0000-000000000305', 'OUTFLOW-202602-900002', DATE '2026-02-25', 'OUTFLOW', 14500000.00, 'IDR', 1, 14500000.00, '00000000-0000-0000-0000-000000000201', (SELECT id FROM departments WHERE code = 'OPS'), (SELECT id FROM cashflow_categories WHERE name = 'Rent and Utilities' AND direction = 'OUTFLOW'), (SELECT id FROM payment_methods WHERE name = 'Bank Transfer'), 'Graha Sudirman Building', 'RENT-2026-002', 'Office rent and utilities for February.', 'APPROVED', '00000000-0000-0000-0000-000000000104', TIMESTAMPTZ '2026-02-24 15:00:00+07', '00000000-0000-0000-0000-000000000101', TIMESTAMPTZ '2026-02-25 08:45:00+07', NULL, NULL, TIMESTAMPTZ '2026-02-24 14:30:00+07', TIMESTAMPTZ '2026-02-25 08:45:00+07'),
  ('00000000-0000-0000-0000-000000000306', 'INFLOW-202603-900001', DATE '2026-03-12', 'INFLOW', 156000000.00, 'IDR', 1, 156000000.00, '00000000-0000-0000-0000-000000000201', (SELECT id FROM departments WHERE code = 'SAL'), (SELECT id FROM cashflow_categories WHERE name = 'Product Sales' AND direction = 'INFLOW'), (SELECT id FROM payment_methods WHERE name = 'Bank Transfer'), 'CV Maju Bersama', 'INV-2026-031', 'March distributor payment.', 'APPROVED', '00000000-0000-0000-0000-000000000105', TIMESTAMPTZ '2026-03-12 10:30:00+07', '00000000-0000-0000-0000-000000000101', TIMESTAMPTZ '2026-03-12 16:10:00+07', NULL, NULL, TIMESTAMPTZ '2026-03-12 10:05:00+07', TIMESTAMPTZ '2026-03-12 16:10:00+07'),
  ('00000000-0000-0000-0000-000000000307', 'OUTFLOW-202603-900001', DATE '2026-03-20', 'OUTFLOW', 19250000.00, 'IDR', 1, 19250000.00, '00000000-0000-0000-0000-000000000201', (SELECT id FROM departments WHERE code = 'SAL'), (SELECT id FROM cashflow_categories WHERE name = 'Marketing Expense' AND direction = 'OUTFLOW'), (SELECT id FROM payment_methods WHERE name = 'Corporate Card'), 'Meta Ads', 'ADS-2026-003', 'March performance marketing campaign.', 'APPROVED', '00000000-0000-0000-0000-000000000105', TIMESTAMPTZ '2026-03-20 12:00:00+07', '00000000-0000-0000-0000-000000000101', TIMESTAMPTZ '2026-03-20 17:00:00+07', NULL, NULL, TIMESTAMPTZ '2026-03-20 11:30:00+07', TIMESTAMPTZ '2026-03-20 17:00:00+07'),
  ('00000000-0000-0000-0000-000000000308', 'OUTFLOW-202603-900002', DATE '2026-03-28', 'OUTFLOW', 59500000.00, 'IDR', 1, 59500000.00, '00000000-0000-0000-0000-000000000202', (SELECT id FROM departments WHERE code = 'FIN'), (SELECT id FROM cashflow_categories WHERE name = 'Payroll' AND direction = 'OUTFLOW'), (SELECT id FROM payment_methods WHERE name = 'Bank Transfer'), 'March Payroll Batch', 'PAY-2026-003', 'March employee payroll.', 'APPROVED', '00000000-0000-0000-0000-000000000101', TIMESTAMPTZ '2026-03-27 15:00:00+07', '00000000-0000-0000-0000-000000000101', TIMESTAMPTZ '2026-03-28 09:00:00+07', NULL, NULL, TIMESTAMPTZ '2026-03-27 14:50:00+07', TIMESTAMPTZ '2026-03-28 09:00:00+07'),
  ('00000000-0000-0000-0000-000000000309', 'INFLOW-202604-900001', DATE '2026-04-08', 'INFLOW', 139800000.00, 'IDR', 1, 139800000.00, '00000000-0000-0000-0000-000000000201', (SELECT id FROM departments WHERE code = 'SAL'), (SELECT id FROM cashflow_categories WHERE name = 'Service Revenue' AND direction = 'INFLOW'), (SELECT id FROM payment_methods WHERE name = 'Bank Transfer'), 'PT Solusi Awan', 'INV-2026-047', 'Monthly managed service revenue.', 'APPROVED', '00000000-0000-0000-0000-000000000105', TIMESTAMPTZ '2026-04-08 10:45:00+07', '00000000-0000-0000-0000-000000000101', TIMESTAMPTZ '2026-04-08 15:10:00+07', NULL, NULL, TIMESTAMPTZ '2026-04-08 10:20:00+07', TIMESTAMPTZ '2026-04-08 15:10:00+07'),
  ('00000000-0000-0000-0000-000000000310', 'OUTFLOW-202604-900001', DATE '2026-04-17', 'OUTFLOW', 41300000.00, 'IDR', 1, 41300000.00, '00000000-0000-0000-0000-000000000201', (SELECT id FROM departments WHERE code = 'OPS'), (SELECT id FROM cashflow_categories WHERE name = 'Vendor Payments' AND direction = 'OUTFLOW'), (SELECT id FROM payment_methods WHERE name = 'Bank Transfer'), 'PT Infrastruktur Data', 'BILL-IT-041', 'Cloud infrastructure vendor invoice.', 'APPROVED', '00000000-0000-0000-0000-000000000104', TIMESTAMPTZ '2026-04-17 09:45:00+07', '00000000-0000-0000-0000-000000000101', TIMESTAMPTZ '2026-04-17 13:30:00+07', NULL, NULL, TIMESTAMPTZ '2026-04-17 09:10:00+07', TIMESTAMPTZ '2026-04-17 13:30:00+07'),
  ('00000000-0000-0000-0000-000000000311', 'OUTFLOW-202604-900002', DATE '2026-04-30', 'OUTFLOW', 21000000.00, 'IDR', 1, 21000000.00, '00000000-0000-0000-0000-000000000201', (SELECT id FROM departments WHERE code = 'FIN'), (SELECT id FROM cashflow_categories WHERE name = 'Tax' AND direction = 'OUTFLOW'), (SELECT id FROM payment_methods WHERE name = 'Bank Transfer'), 'Direktorat Jenderal Pajak', 'TAX-2026-Q1', 'Quarterly tax payment.', 'APPROVED', '00000000-0000-0000-0000-000000000101', TIMESTAMPTZ '2026-04-29 14:15:00+07', '00000000-0000-0000-0000-000000000101', TIMESTAMPTZ '2026-04-30 09:10:00+07', NULL, NULL, TIMESTAMPTZ '2026-04-29 14:00:00+07', TIMESTAMPTZ '2026-04-30 09:10:00+07'),
  ('00000000-0000-0000-0000-000000000312', 'INFLOW-202605-900001', DATE '2026-05-11', 'INFLOW', 171400000.00, 'IDR', 1, 171400000.00, '00000000-0000-0000-0000-000000000201', (SELECT id FROM departments WHERE code = 'SAL'), (SELECT id FROM cashflow_categories WHERE name = 'Product Sales' AND direction = 'INFLOW'), (SELECT id FROM payment_methods WHERE name = 'Bank Transfer'), 'PT Nusantara Retail', 'INV-2026-062', 'May retail channel settlement.', 'APPROVED', '00000000-0000-0000-0000-000000000105', TIMESTAMPTZ '2026-05-11 10:20:00+07', '00000000-0000-0000-0000-000000000101', TIMESTAMPTZ '2026-05-11 15:00:00+07', NULL, NULL, TIMESTAMPTZ '2026-05-11 10:00:00+07', TIMESTAMPTZ '2026-05-11 15:00:00+07'),
  ('00000000-0000-0000-0000-000000000313', 'OUTFLOW-202605-900001', DATE '2026-05-19', 'OUTFLOW', 22750000.00, 'IDR', 1, 22750000.00, '00000000-0000-0000-0000-000000000201', (SELECT id FROM departments WHERE code = 'SAL'), (SELECT id FROM cashflow_categories WHERE name = 'Marketing Expense' AND direction = 'OUTFLOW'), (SELECT id FROM payment_methods WHERE name = 'Corporate Card'), 'Google Ads', 'ADS-2026-005', 'May acquisition campaign.', 'APPROVED', '00000000-0000-0000-0000-000000000105', TIMESTAMPTZ '2026-05-19 13:00:00+07', '00000000-0000-0000-0000-000000000101', TIMESTAMPTZ '2026-05-19 16:40:00+07', NULL, NULL, TIMESTAMPTZ '2026-05-19 12:40:00+07', TIMESTAMPTZ '2026-05-19 16:40:00+07'),
  ('00000000-0000-0000-0000-000000000314', 'OUTFLOW-202605-900002', DATE '2026-05-28', 'OUTFLOW', 60000000.00, 'IDR', 1, 60000000.00, '00000000-0000-0000-0000-000000000202', (SELECT id FROM departments WHERE code = 'FIN'), (SELECT id FROM cashflow_categories WHERE name = 'Payroll' AND direction = 'OUTFLOW'), (SELECT id FROM payment_methods WHERE name = 'Bank Transfer'), 'May Payroll Batch', 'PAY-2026-005', 'May employee payroll.', 'APPROVED', '00000000-0000-0000-0000-000000000101', TIMESTAMPTZ '2026-05-27 15:20:00+07', '00000000-0000-0000-0000-000000000101', TIMESTAMPTZ '2026-05-28 09:00:00+07', NULL, NULL, TIMESTAMPTZ '2026-05-27 15:00:00+07', TIMESTAMPTZ '2026-05-28 09:00:00+07'),
  ('00000000-0000-0000-0000-000000000315', 'INFLOW-202606-900001', DATE '2026-06-09', 'INFLOW', 186900000.00, 'IDR', 1, 186900000.00, '00000000-0000-0000-0000-000000000201', (SELECT id FROM departments WHERE code = 'SAL'), (SELECT id FROM cashflow_categories WHERE name = 'Product Sales' AND direction = 'INFLOW'), (SELECT id FROM payment_methods WHERE name = 'Bank Transfer'), 'PT Global Mart', 'INV-2026-077', 'June modern trade settlement.', 'APPROVED', '00000000-0000-0000-0000-000000000105', TIMESTAMPTZ '2026-06-09 11:15:00+07', '00000000-0000-0000-0000-000000000101', TIMESTAMPTZ '2026-06-09 16:20:00+07', NULL, NULL, TIMESTAMPTZ '2026-06-09 10:50:00+07', TIMESTAMPTZ '2026-06-09 16:20:00+07'),
  ('00000000-0000-0000-0000-000000000316', 'OUTFLOW-202606-900001', DATE '2026-06-16', 'OUTFLOW', 36600000.00, 'IDR', 1, 36600000.00, '00000000-0000-0000-0000-000000000201', (SELECT id FROM departments WHERE code = 'OPS'), (SELECT id FROM cashflow_categories WHERE name = 'Vendor Payments' AND direction = 'OUTFLOW'), (SELECT id FROM payment_methods WHERE name = 'Bank Transfer'), 'PT Logistik Prima', 'BILL-OPS-061', 'June fulfillment and delivery cost.', 'APPROVED', '00000000-0000-0000-0000-000000000104', TIMESTAMPTZ '2026-06-16 09:25:00+07', '00000000-0000-0000-0000-000000000101', TIMESTAMPTZ '2026-06-16 13:15:00+07', NULL, NULL, TIMESTAMPTZ '2026-06-16 09:00:00+07', TIMESTAMPTZ '2026-06-16 13:15:00+07'),
  ('00000000-0000-0000-0000-000000000317', 'INFLOW-202606-900002', DATE '2026-06-21', 'INFLOW', 2350000.00, 'IDR', 1, 2350000.00, '00000000-0000-0000-0000-000000000201', (SELECT id FROM departments WHERE code = 'FIN'), (SELECT id FROM cashflow_categories WHERE name = 'Interest Income' AND direction = 'INFLOW'), (SELECT id FROM payment_methods WHERE name = 'Bank Transfer'), 'BCA', 'INT-2026-006', 'Bank interest income.', 'APPROVED', '00000000-0000-0000-0000-000000000101', TIMESTAMPTZ '2026-06-21 10:00:00+07', '00000000-0000-0000-0000-000000000101', TIMESTAMPTZ '2026-06-21 10:30:00+07', NULL, NULL, TIMESTAMPTZ '2026-06-21 09:50:00+07', TIMESTAMPTZ '2026-06-21 10:30:00+07'),
  ('00000000-0000-0000-0000-000000000318', 'OUTFLOW-202606-900002', DATE '2026-06-28', 'OUTFLOW', 62000000.00, 'IDR', 1, 62000000.00, '00000000-0000-0000-0000-000000000202', (SELECT id FROM departments WHERE code = 'FIN'), (SELECT id FROM cashflow_categories WHERE name = 'Payroll' AND direction = 'OUTFLOW'), (SELECT id FROM payment_methods WHERE name = 'Bank Transfer'), 'June Payroll Batch', 'PAY-2026-006', 'June employee payroll.', 'APPROVED', '00000000-0000-0000-0000-000000000101', TIMESTAMPTZ '2026-06-27 15:20:00+07', '00000000-0000-0000-0000-000000000101', TIMESTAMPTZ '2026-06-28 09:00:00+07', NULL, NULL, TIMESTAMPTZ '2026-06-27 15:00:00+07', TIMESTAMPTZ '2026-06-28 09:00:00+07'),
  ('00000000-0000-0000-0000-000000000319', 'INFLOW-202607-900001', DATE '2026-07-03', 'INFLOW', 94750000.00, 'IDR', 1, 94750000.00, '00000000-0000-0000-0000-000000000201', (SELECT id FROM departments WHERE code = 'SAL'), (SELECT id FROM cashflow_categories WHERE name = 'Service Revenue' AND direction = 'INFLOW'), (SELECT id FROM payment_methods WHERE name = 'Bank Transfer'), 'PT Sinar Digital', 'INV-2026-083', 'July service retainer.', 'APPROVED', '00000000-0000-0000-0000-000000000105', TIMESTAMPTZ '2026-07-03 10:40:00+07', '00000000-0000-0000-0000-000000000101', TIMESTAMPTZ '2026-07-03 14:10:00+07', NULL, NULL, TIMESTAMPTZ '2026-07-03 10:15:00+07', TIMESTAMPTZ '2026-07-03 14:10:00+07'),
  ('00000000-0000-0000-0000-000000000320', 'OUTFLOW-202607-900001', DATE '2026-07-04', 'OUTFLOW', 4850000.00, 'IDR', 1, 4850000.00, '00000000-0000-0000-0000-000000000203', (SELECT id FROM departments WHERE code = 'OPS'), (SELECT id FROM cashflow_categories WHERE name = 'Office Supplies' AND direction = 'OUTFLOW'), (SELECT id FROM payment_methods WHERE name = 'Cash'), 'Toko ATK Jakarta', 'PC-2026-017', 'Office supplies replenishment.', 'APPROVED', '00000000-0000-0000-0000-000000000104', TIMESTAMPTZ '2026-07-04 11:00:00+07', '00000000-0000-0000-0000-000000000101', TIMESTAMPTZ '2026-07-04 16:15:00+07', NULL, NULL, TIMESTAMPTZ '2026-07-04 10:35:00+07', TIMESTAMPTZ '2026-07-04 16:15:00+07'),
  ('00000000-0000-0000-0000-000000000321', 'OUTFLOW-202607-900002', DATE '2026-07-05', 'OUTFLOW', 52000000.00, 'IDR', 1, 52000000.00, '00000000-0000-0000-0000-000000000201', (SELECT id FROM departments WHERE code = 'OPS'), (SELECT id FROM cashflow_categories WHERE name = 'Vendor Payments' AND direction = 'OUTFLOW'), (SELECT id FROM payment_methods WHERE name = 'Bank Transfer'), 'PT Mesin Nusantara', 'CAPEX-2026-004', 'Submitted equipment purchase awaiting approval.', 'SUBMITTED', '00000000-0000-0000-0000-000000000104', TIMESTAMPTZ '2026-07-05 09:45:00+07', NULL, NULL, NULL, NULL, TIMESTAMPTZ '2026-07-05 09:20:00+07', TIMESTAMPTZ '2026-07-05 09:45:00+07'),
  ('00000000-0000-0000-0000-000000000322', 'OUTFLOW-202607-900003', DATE '2026-07-05', 'OUTFLOW', 6700000.00, 'IDR', 1, 6700000.00, '00000000-0000-0000-0000-000000000201', (SELECT id FROM departments WHERE code = 'SAL'), (SELECT id FROM cashflow_categories WHERE name = 'Travel and Entertainment' AND direction = 'OUTFLOW'), (SELECT id FROM payment_methods WHERE name = 'Corporate Card'), 'Garuda Indonesia', 'TRV-2026-011', 'Submitted sales travel claim awaiting approval.', 'SUBMITTED', '00000000-0000-0000-0000-000000000105', TIMESTAMPTZ '2026-07-05 10:30:00+07', NULL, NULL, NULL, NULL, TIMESTAMPTZ '2026-07-05 10:05:00+07', TIMESTAMPTZ '2026-07-05 10:30:00+07'),
  ('00000000-0000-0000-0000-000000000323', 'OUTFLOW-202607-900004', DATE '2026-07-05', 'OUTFLOW', 850000.00, 'IDR', 1, 850000.00, '00000000-0000-0000-0000-000000000203', (SELECT id FROM departments WHERE code = 'OPS'), (SELECT id FROM cashflow_categories WHERE name = 'Office Supplies' AND direction = 'OUTFLOW'), (SELECT id FROM payment_methods WHERE name = 'Cash'), 'Toko ATK Jakarta', 'PC-DRAFT-001', 'Draft petty cash request for pantry supplies.', 'DRAFT', '00000000-0000-0000-0000-000000000104', NULL, NULL, NULL, NULL, NULL, TIMESTAMPTZ '2026-07-05 11:00:00+07', TIMESTAMPTZ '2026-07-05 11:00:00+07'),
  ('00000000-0000-0000-0000-000000000324', 'OUTFLOW-202607-900005', DATE '2026-07-02', 'OUTFLOW', 8400000.00, 'IDR', 1, 8400000.00, '00000000-0000-0000-0000-000000000201', (SELECT id FROM departments WHERE code = 'SAL'), (SELECT id FROM cashflow_categories WHERE name = 'Travel and Entertainment' AND direction = 'OUTFLOW'), (SELECT id FROM payment_methods WHERE name = 'Corporate Card'), 'Hotel Tentrem', 'TRV-2026-009', 'Rejected travel reimbursement missing hotel receipt.', 'REJECTED', '00000000-0000-0000-0000-000000000105', TIMESTAMPTZ '2026-07-02 10:00:00+07', '00000000-0000-0000-0000-000000000101', TIMESTAMPTZ '2026-07-02 15:45:00+07', 'Missing hotel receipt attachment.', NULL, TIMESTAMPTZ '2026-07-02 09:30:00+07', TIMESTAMPTZ '2026-07-02 15:45:00+07'),
  ('00000000-0000-0000-0000-000000000325', 'INFLOW-202606-900003', DATE '2026-06-25', 'INFLOW', 12000000.00, 'IDR', 1, 12000000.00, '00000000-0000-0000-0000-000000000201', (SELECT id FROM departments WHERE code = 'FIN'), (SELECT id FROM cashflow_categories WHERE name = 'Interest Income' AND direction = 'INFLOW'), (SELECT id FROM payment_methods WHERE name = 'Bank Transfer'), 'BCA', 'DUP-INT-2026-006', 'Voided duplicate bank interest entry.', 'VOIDED', '00000000-0000-0000-0000-000000000101', TIMESTAMPTZ '2026-06-25 10:00:00+07', '00000000-0000-0000-0000-000000000101', TIMESTAMPTZ '2026-06-25 10:15:00+07', NULL, 'Duplicate bank statement import.', TIMESTAMPTZ '2026-06-25 09:50:00+07', TIMESTAMPTZ '2026-06-25 10:45:00+07'),
  ('00000000-0000-0000-0000-000000000326', 'OUTFLOW-202607-900006', DATE '2026-07-01', 'OUTFLOW', 13500000.00, 'IDR', 1, 13500000.00, '00000000-0000-0000-0000-000000000201', (SELECT id FROM departments WHERE code = 'OPS'), (SELECT id FROM cashflow_categories WHERE name = 'Rent and Utilities' AND direction = 'OUTFLOW'), (SELECT id FROM payment_methods WHERE name = 'Bank Transfer'), 'Graha Sudirman Building', 'RENT-2026-007', 'July office rent.', 'APPROVED', '00000000-0000-0000-0000-000000000104', TIMESTAMPTZ '2026-07-01 09:30:00+07', '00000000-0000-0000-0000-000000000101', TIMESTAMPTZ '2026-07-01 13:00:00+07', NULL, NULL, TIMESTAMPTZ '2026-07-01 09:00:00+07', TIMESTAMPTZ '2026-07-01 13:00:00+07')
ON CONFLICT (id) DO UPDATE SET
  transaction_no = EXCLUDED.transaction_no,
  transaction_date = EXCLUDED.transaction_date,
  direction = EXCLUDED.direction,
  amount = EXCLUDED.amount,
  currency = EXCLUDED.currency,
  exchange_rate = EXCLUDED.exchange_rate,
  base_amount = EXCLUDED.base_amount,
  cash_account_id = EXCLUDED.cash_account_id,
  department_id = EXCLUDED.department_id,
  category_id = EXCLUDED.category_id,
  payment_method_id = EXCLUDED.payment_method_id,
  counterparty_name = EXCLUDED.counterparty_name,
  reference_no = EXCLUDED.reference_no,
  description = EXCLUDED.description,
  status = EXCLUDED.status,
  created_by = EXCLUDED.created_by,
  submitted_at = EXCLUDED.submitted_at,
  reviewed_by = EXCLUDED.reviewed_by,
  reviewed_at = EXCLUDED.reviewed_at,
  rejection_reason = EXCLUDED.rejection_reason,
  void_reason = EXCLUDED.void_reason,
  created_at = EXCLUDED.created_at,
  updated_at = EXCLUDED.updated_at;

-- Keep demo notifications/audit logs idempotent without touching unrelated QA data.
CREATE TEMP TABLE seed_demo_transaction_ids (id UUID PRIMARY KEY) ON COMMIT DROP;

INSERT INTO seed_demo_transaction_ids (id)
VALUES
  ('00000000-0000-0000-0000-000000000301'),
  ('00000000-0000-0000-0000-000000000302'),
  ('00000000-0000-0000-0000-000000000303'),
  ('00000000-0000-0000-0000-000000000304'),
  ('00000000-0000-0000-0000-000000000305'),
  ('00000000-0000-0000-0000-000000000306'),
  ('00000000-0000-0000-0000-000000000307'),
  ('00000000-0000-0000-0000-000000000308'),
  ('00000000-0000-0000-0000-000000000309'),
  ('00000000-0000-0000-0000-000000000310'),
  ('00000000-0000-0000-0000-000000000311'),
  ('00000000-0000-0000-0000-000000000312'),
  ('00000000-0000-0000-0000-000000000313'),
  ('00000000-0000-0000-0000-000000000314'),
  ('00000000-0000-0000-0000-000000000315'),
  ('00000000-0000-0000-0000-000000000316'),
  ('00000000-0000-0000-0000-000000000317'),
  ('00000000-0000-0000-0000-000000000318'),
  ('00000000-0000-0000-0000-000000000319'),
  ('00000000-0000-0000-0000-000000000320'),
  ('00000000-0000-0000-0000-000000000321'),
  ('00000000-0000-0000-0000-000000000322'),
  ('00000000-0000-0000-0000-000000000323'),
  ('00000000-0000-0000-0000-000000000324'),
  ('00000000-0000-0000-0000-000000000325'),
  ('00000000-0000-0000-0000-000000000326');

DELETE FROM transaction_audit_logs
WHERE transaction_id IN (SELECT id FROM seed_demo_transaction_ids);

INSERT INTO transaction_audit_logs (
  transaction_id,
  actor_user_id,
  action,
  old_value,
  new_value,
  reason,
  created_at
)
SELECT
  t.id,
  t.created_by,
  'CREATE',
  NULL,
  jsonb_build_object('status', 'DRAFT', 'amount', t.amount, 'direction', t.direction),
  NULL,
  t.created_at
FROM cashflow_transactions t
WHERE t.id IN (SELECT id FROM seed_demo_transaction_ids);

INSERT INTO transaction_audit_logs (
  transaction_id,
  actor_user_id,
  action,
  old_value,
  new_value,
  reason,
  created_at
)
SELECT
  t.id,
  t.created_by,
  'SUBMIT',
  jsonb_build_object('status', 'DRAFT'),
  jsonb_build_object('status', 'SUBMITTED', 'submitted_at', t.submitted_at),
  NULL,
  COALESCE(t.submitted_at, t.created_at + INTERVAL '15 minutes')
FROM cashflow_transactions t
WHERE t.id IN (SELECT id FROM seed_demo_transaction_ids)
  AND t.status IN ('SUBMITTED', 'APPROVED', 'REJECTED', 'VOIDED');

INSERT INTO transaction_audit_logs (
  transaction_id,
  actor_user_id,
  action,
  old_value,
  new_value,
  reason,
  created_at
)
SELECT
  t.id,
  COALESCE(t.reviewed_by, '00000000-0000-0000-0000-000000000101'),
  'APPROVE',
  jsonb_build_object('status', 'SUBMITTED'),
  jsonb_build_object('status', 'APPROVED', 'reviewed_by', COALESCE(t.reviewed_by, '00000000-0000-0000-0000-000000000101'), 'reviewed_at', t.reviewed_at),
  NULL,
  COALESCE(t.reviewed_at, t.created_at + INTERVAL '30 minutes')
FROM cashflow_transactions t
WHERE t.id IN (SELECT id FROM seed_demo_transaction_ids)
  AND t.status IN ('APPROVED', 'VOIDED');

INSERT INTO transaction_audit_logs (
  transaction_id,
  actor_user_id,
  action,
  old_value,
  new_value,
  reason,
  created_at
)
SELECT
  t.id,
  t.reviewed_by,
  'REJECT',
  jsonb_build_object('status', 'SUBMITTED'),
  jsonb_build_object('status', 'REJECTED', 'rejection_reason', t.rejection_reason),
  t.rejection_reason,
  t.reviewed_at
FROM cashflow_transactions t
WHERE t.id IN (SELECT id FROM seed_demo_transaction_ids)
  AND t.status = 'REJECTED';

INSERT INTO transaction_audit_logs (
  transaction_id,
  actor_user_id,
  action,
  old_value,
  new_value,
  reason,
  created_at
)
SELECT
  t.id,
  COALESCE(t.reviewed_by, '00000000-0000-0000-0000-000000000101'),
  'VOID',
  jsonb_build_object('status', 'APPROVED'),
  jsonb_build_object('status', 'VOIDED', 'void_reason', t.void_reason),
  t.void_reason,
  t.updated_at
FROM cashflow_transactions t
WHERE t.id IN (SELECT id FROM seed_demo_transaction_ids)
  AND t.status = 'VOIDED';

DELETE FROM notifications
WHERE user_id = '00000000-0000-0000-0000-000000000101'
  AND type = 'PENDING_APPROVAL'
  AND related_transaction_id IN (
    '00000000-0000-0000-0000-000000000321',
    '00000000-0000-0000-0000-000000000322'
  );

INSERT INTO notifications (
  id,
  user_id,
  type,
  title,
  message,
  related_transaction_id,
  is_read,
  created_at
)
VALUES
  ('00000000-0000-0000-0000-000000000401', '00000000-0000-0000-0000-000000000101', 'PENDING_APPROVAL', 'Transaction awaiting approval', 'OUTFLOW-202607-900002 from Operations requires Finance review.', '00000000-0000-0000-0000-000000000321', false, TIMESTAMPTZ '2026-07-05 09:45:30+07'),
  ('00000000-0000-0000-0000-000000000402', '00000000-0000-0000-0000-000000000101', 'PENDING_APPROVAL', 'Transaction awaiting approval', 'OUTFLOW-202607-900003 from Sales requires Finance review.', '00000000-0000-0000-0000-000000000322', false, TIMESTAMPTZ '2026-07-05 10:30:30+07')
ON CONFLICT (id) DO UPDATE SET
  user_id = EXCLUDED.user_id,
  title = EXCLUDED.title,
  message = EXCLUDED.message,
  related_transaction_id = EXCLUDED.related_transaction_id,
  is_read = EXCLUDED.is_read,
  created_at = EXCLUDED.created_at;

-- Optional recurring templates for later recurring-transaction QA.
INSERT INTO recurring_transaction_templates (
  id,
  department_id,
  category_id,
  cash_account_id,
  payment_method_id,
  direction,
  amount,
  currency,
  counterparty_name,
  reference_no,
  description,
  submission_mode,
  frequency,
  interval,
  next_run_date,
  end_date,
  is_active,
  created_by,
  created_at,
  updated_at
)
VALUES
  ('00000000-0000-0000-0000-000000000501', (SELECT id FROM departments WHERE code = 'OPS'), (SELECT id FROM cashflow_categories WHERE name = 'Rent and Utilities' AND direction = 'OUTFLOW'), '00000000-0000-0000-0000-000000000201', (SELECT id FROM payment_methods WHERE name = 'Bank Transfer'), 'OUTFLOW', 13500000.00, 'IDR', 'Graha Sudirman Building', 'RENT-MONTHLY', 'Monthly office rent template.', 'AUTO_SUBMIT', 'MONTHLY', 1, DATE '2026-08-01', NULL, true, '00000000-0000-0000-0000-000000000101', now(), now()),
  ('00000000-0000-0000-0000-000000000502', (SELECT id FROM departments WHERE code = 'SAL'), (SELECT id FROM cashflow_categories WHERE name = 'Marketing Expense' AND direction = 'OUTFLOW'), '00000000-0000-0000-0000-000000000201', (SELECT id FROM payment_methods WHERE name = 'Corporate Card'), 'OUTFLOW', 20000000.00, 'IDR', 'Campaign Budget', 'MKT-MONTHLY', 'Monthly draft reminder for paid acquisition budget.', 'DRAFT', 'MONTHLY', 1, DATE '2026-08-05', NULL, true, '00000000-0000-0000-0000-000000000105', now(), now())
ON CONFLICT (id) DO UPDATE SET
  department_id = EXCLUDED.department_id,
  category_id = EXCLUDED.category_id,
  cash_account_id = EXCLUDED.cash_account_id,
  payment_method_id = EXCLUDED.payment_method_id,
  direction = EXCLUDED.direction,
  amount = EXCLUDED.amount,
  currency = EXCLUDED.currency,
  counterparty_name = EXCLUDED.counterparty_name,
  reference_no = EXCLUDED.reference_no,
  description = EXCLUDED.description,
  submission_mode = EXCLUDED.submission_mode,
  frequency = EXCLUDED.frequency,
  interval = EXCLUDED.interval,
  next_run_date = EXCLUDED.next_run_date,
  end_date = EXCLUDED.end_date,
  is_active = EXCLUDED.is_active,
  created_by = EXCLUDED.created_by,
  updated_at = now();

COMMIT;
