CREATE TABLE cashflow_transactions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  transaction_no VARCHAR(60) NOT NULL UNIQUE,
  transaction_date DATE NOT NULL,
  direction VARCHAR(20) NOT NULL CHECK (
    direction IN ('INFLOW', 'OUTFLOW')
  ),
  amount NUMERIC(18,2) NOT NULL CHECK (amount > 0),
  currency CHAR(3) NOT NULL DEFAULT 'IDR',
  exchange_rate NUMERIC(18,6) NOT NULL DEFAULT 1,
  base_amount NUMERIC(18,2) NOT NULL,
  cash_account_id UUID NOT NULL REFERENCES cash_accounts(id),
  department_id UUID NOT NULL REFERENCES departments(id),
  category_id UUID NOT NULL REFERENCES cashflow_categories(id),
  payment_method_id UUID NULL REFERENCES payment_methods(id),
  counterparty_name VARCHAR(180) NULL,
  reference_no VARCHAR(120) NULL,
  description TEXT NULL,
  status VARCHAR(30) NOT NULL CHECK (
    status IN ('DRAFT', 'SUBMITTED', 'APPROVED', 'REJECTED', 'VOIDED')
  ),
  created_by UUID NOT NULL REFERENCES user_profiles(id),
  submitted_at TIMESTAMPTZ NULL,
  reviewed_by UUID NULL REFERENCES user_profiles(id),
  reviewed_at TIMESTAMPTZ NULL,
  rejection_reason TEXT NULL,
  void_reason TEXT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_cashflow_report
ON cashflow_transactions (
  status,
  transaction_date,
  direction,
  department_id,
  category_id,
  cash_account_id
);
