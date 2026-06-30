from typing import Annotated, Any, cast

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from supabase import Client

from app.core.config import Settings, get_settings
from app.core.models import CurrentUser, Role, UserStatus
from app.core.supabase_client import get_supabase_client

bearer = HTTPBearer(auto_error=True)


def decode_access_token(token: str, jwt_secret: str) -> dict[str, object]:
    if not jwt_secret:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="JWT_SECRET is not configured",
        )
    try:
        decoded = jwt.decode(
            token,
            jwt_secret,
            algorithms=["HS256"],
            audience="authenticated",
        )
        return cast(dict[str, object], decoded)
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token"
        ) from exc


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer)],
    settings: Annotated[Settings, Depends(get_settings)],
    db: Annotated[Client, Depends(get_supabase_client)],
) -> CurrentUser:
    claims = decode_access_token(credentials.credentials, settings.jwt_secret)
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