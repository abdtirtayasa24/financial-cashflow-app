-- Maintain updated_at automatically on every table that has the column,
-- regardless of how the update happens (app, cron, or manual SQL).

CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$;

CREATE TRIGGER trg_user_profiles_updated_at
  BEFORE UPDATE ON user_profiles
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_cashflow_transactions_updated_at
  BEFORE UPDATE ON cashflow_transactions
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_app_settings_updated_at
  BEFORE UPDATE ON app_settings
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_recurring_transaction_templates_updated_at
  BEFORE UPDATE ON recurring_transaction_templates
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();