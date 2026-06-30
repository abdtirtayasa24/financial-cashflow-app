CREATE TABLE report_snapshots (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  report_type VARCHAR(80) NOT NULL,
  date_from DATE NOT NULL,
  date_to DATE NOT NULL,
  filters JSONB NULL,
  result JSONB NOT NULL,
  generated_by UUID NULL REFERENCES user_profiles(id),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
