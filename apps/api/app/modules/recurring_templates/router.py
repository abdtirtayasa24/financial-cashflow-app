from typing import Annotated

from fastapi import APIRouter, Depends, status
from supabase import Client

from app.core.auth import get_current_user
from app.core.models import CurrentUser
from app.core.supabase_client import get_supabase_client
from app.modules.recurring_templates.schemas import (
    RecurringTemplateCreate,
    RecurringTemplateOut,
    RecurringTemplateUpdate,
)
from app.modules.recurring_templates.service import RecurringTemplateService

router = APIRouter(prefix="/recurring-templates", tags=["Recurring Templates"])

CurrentUserDep = Annotated[CurrentUser, Depends(get_current_user)]


@router.get("", response_model=list[RecurringTemplateOut])
async def list_templates(
    db: Annotated[Client, Depends(get_supabase_client)],
    user: CurrentUserDep,
) -> list[RecurringTemplateOut]:
    return RecurringTemplateService(db).list(user)


@router.get("/{template_id}", response_model=RecurringTemplateOut)
async def get_template(
    template_id: str,
    db: Annotated[Client, Depends(get_supabase_client)],
    user: CurrentUserDep,
) -> RecurringTemplateOut:
    return RecurringTemplateService(db).get(template_id, user)


@router.post("", response_model=RecurringTemplateOut, status_code=status.HTTP_201_CREATED)
async def create_template(
    data: RecurringTemplateCreate,
    db: Annotated[Client, Depends(get_supabase_client)],
    user: CurrentUserDep,
) -> RecurringTemplateOut:
    return RecurringTemplateService(db).create(data, user)


@router.patch("/{template_id}", response_model=RecurringTemplateOut)
async def update_template(
    template_id: str,
    data: RecurringTemplateUpdate,
    db: Annotated[Client, Depends(get_supabase_client)],
    user: CurrentUserDep,
) -> RecurringTemplateOut:
    return RecurringTemplateService(db).update(template_id, data, user)


@router.post("/{template_id}/deactivate", response_model=RecurringTemplateOut)
async def deactivate_template(
    template_id: str,
    db: Annotated[Client, Depends(get_supabase_client)],
    user: CurrentUserDep,
) -> RecurringTemplateOut:
    return RecurringTemplateService(db).deactivate(template_id, user)
