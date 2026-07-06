from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client

from app.core.auth import require_roles
from app.core.models import CurrentUser, Role
from app.core.supabase_client import get_supabase_client
from app.modules.app_settings.schemas import AppSettingOut, AppSettingUpsert
from app.modules.app_settings.service import AppSettingService

router = APIRouter(prefix="/settings", tags=["App Settings"])

SysAdmin = Annotated[
    CurrentUser, Depends(require_roles(Role.SYSTEM_ADMIN, Role.MANAGEMENT))
]


def _not_found() -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not found")


@router.get("", response_model=list[AppSettingOut])
async def list_settings(
    db: Annotated[Client, Depends(get_supabase_client)],
    _: SysAdmin,
) -> list[AppSettingOut]:
    return AppSettingService(db).list()


@router.get("/{key}", response_model=AppSettingOut)
async def get_setting(
    key: str,
    db: Annotated[Client, Depends(get_supabase_client)],
    _: SysAdmin,
) -> AppSettingOut:
    setting = AppSettingService(db).get_by_key(key)
    if not setting:
        raise _not_found()
    return setting


@router.put("", response_model=AppSettingOut)
async def upsert_setting(
    data: AppSettingUpsert,
    db: Annotated[Client, Depends(get_supabase_client)],
    actor: SysAdmin,
) -> AppSettingOut:
    return AppSettingService(db).upsert(data, actor.id)