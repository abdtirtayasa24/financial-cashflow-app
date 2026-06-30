from functools import lru_cache

from supabase import Client, create_client

from app.core.config import get_settings


@lru_cache
def get_supabase_client() -> Client:
    """Build the singleton Supabase client using the service-role key.

    This client bypasses Row Level Security and must only ever be used
    server-side. It is constructed lazily so the app can boot (and serve the
    health endpoint) without a live Supabase project configured.
    """
    settings = get_settings()
    return create_client(settings.supabase_url, settings.supabase_service_role_key)