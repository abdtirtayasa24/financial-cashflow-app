CREATE TABLE transaction_attachments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  transaction_id UUID NOT NULL REFERENCES cashflow_transactions(id),
  original_file_name VARCHAR(255) NOT NULL,
  stored_file_name VARCHAR(255) NOT NULL,
  relative_path TEXT NOT NULL,
  mime_type VARCHAR(120) NOT NULL,
  file_size_bytes BIGINT NOT NULL,
  checksum_sha256 VARCHAR(128) NULL,
  uploaded_by UUID NOT NULL REFERENCES user_profiles(id),
  uploaded_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE transaction_audit_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  transaction_id UUID NOT NULL REFERENCES cashflow_transactions(id),
  actor_user_id UUID NOT NULL REFERENCES user_profiles(id),
  action VARCHAR(60) NOT NULL,
  old_value JSONB NULL,
  new_value JSONB NULL,
  reason TEXT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
