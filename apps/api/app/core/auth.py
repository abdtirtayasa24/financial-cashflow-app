from typing import Annotated, Any, cast

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWKClient
from jwt.exceptions import PyJWKClientError, PyJWTError
from supabase import Client

from app.core.config import Settings, get_settings
from app.core.models import CurrentUser, Role, UserStatus
from app.core.supabase_client import get_supabase_client

bearer = HTTPBearer(auto_error=True)

# Asymmetric algorithms verified via the Supabase JWKS endpoint.
_ASYMMETRIC_ALGS = {"RS256", "ES256"}
# Module-level JWKS client cache keyed by URL (PyJWKClient caches keys
# internally with a TTL, so we reuse one client per URL per process).
_jwk_clients: dict[str, PyJWKClient] = {}


def _get_jwk_client(jwks_url: str) -> PyJWKClient:
    client = _jwk_clients.get(jwks_url)
    if client is None:
        client = PyJWKClient(jwks_url)
        _jwk_clients[jwks_url] = client
    return client


def decode_access_token(token: str, settings: Settings) -> dict[str, object]:
    """Verify a Supabase Auth access token (JWKS for asymmetric, HS256 fallback)."""
    try:
        header = jwt.get_unverified_header(token)
    except PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token"
        ) from exc

    alg = header.get("alg")

    try:
        if alg in _ASYMMETRIC_ALGS:
            jwks_url = settings.jwks_url
            if not settings.supabase_url and not settings.supabase_jwks_url:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="JWKS URL is not configured",
                )
            signing_key = _get_jwk_client(jwks_url).get_signing_key_from_jwt(token)
            claims = jwt.decode(
                token,
                signing_key.key,
                algorithms=[alg],
                audience="authenticated",
            )
        elif alg == "HS256":
            if not settings.jwt_secret:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="JWT_SECRET is not configured",
                )
            claims = jwt.decode(
                token,
                settings.jwt_secret,
                algorithms=["HS256"],
                audience="authenticated",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="unsupported token algorithm",
            )
    except (PyJWTError, PyJWKClientError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token"
        ) from exc

    return cast(dict[str, object], claims)


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer)],
    settings: Annotated[Settings, Depends(get_settings)],
    db: Annotated[Client, Depends(get_supabase_client)],
) -> CurrentUser:
    claims = decode_access_token(credentials.credentials, settings)
    sub = claims.get("sub")
    if not isinstance(sub, str):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token"
        )

    resp = db.table("user_profiles").select("*").eq("id", sub).limit(1).execute()
    rows = cast(list[dict[str, Any]], resp.data)
    row = rows[0] if rows else None
    if not row:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="user not found"
        )
    if row.get("status") != UserStatus.ACTIVE.value:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="inactive user"
        )

    email_claim = claims.get("email")
    return CurrentUser(
        id=row["id"],
        role=Role(row["role"]),
        department_id=row.get("department_id"),
        full_name=row["full_name"],
        status=UserStatus(row["status"]),
        email=email_claim if isinstance(email_claim, str) else None,
    )


def require_roles(*roles: Role) -> Any:
    """Dependency factory: allow only the given roles, else 403."""
    allowed = {r.value for r in roles}

    def _check(
        user: Annotated[CurrentUser, Depends(get_current_user)],
    ) -> CurrentUser:
        if user.role.value not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="forbidden"
            )
        return user

    return _check