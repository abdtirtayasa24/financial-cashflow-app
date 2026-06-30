from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    All fields carry defaults so the app imports and runs without a real
    Supabase project configured (e.g. in CI/tests). Real values are supplied
    at runtime via environment variables or a .env file.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Financial Cashflow API"
    app_version: str = "0.1.0"
    api_prefix: str = "/api"

    supabase_url: str = ""
    supabase_service_role_key: str = ""
    supabase_anon_key: str = ""

    # JWT validation config for Supabase Auth tokens.
    # Asymmetric (RS256/ES256) tokens are verified via the JWKS endpoint
    # (derived from supabase_url). HS256 tokens (legacy) fall back to jwt_secret.
    jwt_secret: str = ""
    supabase_jwks_url: str = ""

    upload_dir: str = "/var/app/financial-cashflow/uploads"
    exports_dir: str = "/var/app/financial-cashflow/exports"

    cors_origins: str = "*"

    def get_cors_origins(self) -> list[str]:
        if self.cors_origins.strip() == "*":
            return ["*"]
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def jwks_url(self) -> str:
        if self.supabase_jwks_url:
            return self.supabase_jwks_url
        return f"{self.supabase_url.rstrip('/')}/auth/v1/.well-known/jwks.json"


@lru_cache
def get_settings() -> Settings:
    return Settings()