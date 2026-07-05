-- Backend-only RPC for efficient unread notification counts.
-- The frontend must still access notifications through FastAPI, not Supabase.

CREATE OR REPLACE FUNCTION notification_unread_count(p_user_id UUID)
RETURNS INTEGER
LANGUAGE SQL
STABLE
SECURITY DEFINER
SET search_path = public
AS $$
  SELECT COUNT(*)::INTEGER
  FROM notifications
  WHERE user_id = p_user_id
    AND is_read = FALSE;
$$;

REVOKE ALL ON FUNCTION notification_unread_count(UUID) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION notification_unread_count(UUID) TO service_role;
