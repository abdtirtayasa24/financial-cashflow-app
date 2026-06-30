CREATE TABLE cashflow_categories (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  parent_category_id UUID NULL REFERENCES cashflow_categories(id),
  name VARCHAR(120) NOT NULL,
  direction VARCHAR(20) NOT NULL CHECK (
    direction IN ('INFLOW', 'OUTFLOW', 'BOTH')
  ),
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE(name, direction)
);

CREATE TABLE payment_methods (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(80) NOT NULL UNIQUE,
  is_active BOOLEAN NOT NULL DEFAULT TRUE
);
