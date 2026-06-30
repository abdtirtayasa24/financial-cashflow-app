CREATE TABLE cash_accounts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(120) NOT NULL,
  account_type VARCHAR(40) NOT NULL CHECK (
    account_type IN ('CASH', 'BANK', 'EWALLET', 'OTHER')
  ),
  opening_balance NUMERIC(18,2) NOT NULL DEFAULT 0,
  opening_balance_date DATE NOT NULL,
  currency CHAR(3) NOT NULL DEFAULT 'IDR',
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
