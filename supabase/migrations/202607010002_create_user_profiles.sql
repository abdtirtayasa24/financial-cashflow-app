CREATE TABLE user_profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  department_id UUID NULL REFERENCES departments(id),
  full_name VARCHAR(160) NOT NULL,
  role VARCHAR(40) NOT NULL CHECK (
    role IN (
      'EMPLOYEE',
      'DEPARTMENT_MANAGER',
      'FINANCE_ADMIN',
      'MANAGEMENT',
      'SYSTEM_ADMIN'
    )
  ),
  status VARCHAR(30) NOT NULL DEFAULT 'ACTIVE',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
