from typing import Annotated

from fastapi import APIRouter, Depends, status
from supabase import Client

from app.core.auth import require_roles
from app.core.models import CurrentUser, Role
from app.core.supabase_client import get_supabase_client
from app.modules.users.schemas import UserCreate, UserOut, UserUpdate
from app.modules.users.service import UserService

router = APIRouter(prefix="/users", tags=["Users"])

SysAdmin = Annotated[
    CurrentUser, Depends(require_roles(Role.SYSTEM_ADMIN, Role.MANAGEMENT))
]


@router.get("", response_model=list[UserOut])
async def list_users(
    db: Annotated[Client, Depends(get_supabase_client)],
    _: SysAdmin,
) -> list[UserOut]:
    return UserService(db).list()


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(
    data: UserCreate,
    db: Annotated[Client, Depends(get_supabase_client)],
    _: SysAdmin,
) -> UserOut:
    return UserService(db).create(data)


@router.get("/{user_id}", response_model=UserOut)
async def get_user(
    user_id: str,
    db: Annotated[Client, Depends(get_supabase_client)],
    _: SysAdmin,
) -> UserOut:
    return UserService(db).get(user_id)


@router.patch("/{user_id}", response_model=UserOut)
async def update_user(
    user_id: str,
    data: UserUpdate,
    db: Annotated[Client, Depends(get_supabase_client)],
    _: SysAdmin,
) -> UserOut:
    return UserService(db).update(user_id, data)