-- Enable Row Level Security as a defense-in-depth layer.
-- The backend uses the service-role key, which bypasses RLS, so all app data
-- access goes through FastAPI. RLS here limits damage if the anon key leaks.

ALTER TABLE departments ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE cash_accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE cashflow_categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE payment_methods ENABLE ROW LEVEL SECURITY;
ALTER TABLE cashflow_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE transaction_attachments ENABLE ROW LEVEL SECURITY;
ALTER TABLE transaction_audit_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE report_snapshots ENABLE ROW LEVEL SECURITY;
ALTER TABLE app_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE recurring_transaction_templates ENABLE ROW LEVEL SECURITY;

-- user_profiles is the one table the frontend may read via the Supabase
-- browser client (for session info): a user may read only their own profile.
CREATE POLICY user_profiles_read_own
  ON user_profiles
  FOR SELECT
  TO authenticated
  USING (auth.uid() = id);

-- All other tables intentionally have NO policy. With RLS enabled and no
-- policy, the anon/authenticated roles are denied. All access goes through
-- FastAPI using the service-role key.