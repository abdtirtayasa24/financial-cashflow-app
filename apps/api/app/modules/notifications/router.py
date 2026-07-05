from typing import Annotated

from fastapi import APIRouter, Depends, Query
from supabase import Client

from app.core.auth import get_current_user
from app.core.models import CurrentUser
from app.core.supabase_client import get_supabase_client
from app.modules.notifications.schemas import (
    MarkAllReadOut,
    NotificationOut,
    UnreadCountOut,
)
from app.modules.notifications.service import NotificationService

router = APIRouter(prefix="/notifications", tags=["Notifications"])

UserDep = Annotated[CurrentUser, Depends(get_current_user)]
DbDep = Annotated[Client, Depends(get_supabase_client)]


def _service(db: Client) -> NotificationService:
    return NotificationService(db)


@router.get("", response_model=list[NotificationOut])
async def list_notifications(
    db: DbDep,
    user: UserDep,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[NotificationOut]:
    return _service(db).list(user, limit=limit, offset=offset)


@router.get("/unread-count", response_model=UnreadCountOut)
async def unread_count(db: DbDep, user: UserDep) -> UnreadCountOut:
    return _service(db).unread_count(user)


@router.post("/read-all", response_model=MarkAllReadOut)
async def mark_all_read(db: DbDep, user: UserDep) -> MarkAllReadOut:
    return _service(db).mark_all_read(user)


@router.post("/{notification_id}/read", response_model=NotificationOut)
async def mark_read(
    notification_id: str,
    db: DbDep,
    user: UserDep,
) -> NotificationOut:
    return _service(db).mark_read(notification_id, user)
