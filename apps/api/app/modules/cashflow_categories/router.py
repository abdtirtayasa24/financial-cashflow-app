from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client

from app.core.auth import get_current_user, require_roles
from app.core.models import CurrentUser, Role
from app.core.supabase_client import get_supabase_client
from app.modules.cashflow_categories.schemas import (
    CategoryCreate,
    CategoryOut,
    CategoryUpdate,
)
from app.modules.cashflow_categories.service import CategoryService

router = APIRouter(prefix="/categories", tags=["Cashflow Categories"])

CurrentUserDep = Annotated[CurrentUser, Depends(get_current_user)]
SysAdmin = Annotated[CurrentUser, Depends(require_roles(Role.SYSTEM_ADMIN))]


def _not_found() -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not found")


@router.get("", response_model=list[CategoryOut])
async def list_categories(
    db: Annotated[Client, Depends(get_supabase_client)],
    _: CurrentUserDep,
) -> list[CategoryOut]:
    return CategoryService(db).list()


@router.get("/{category_id}", response_model=CategoryOut)
async def get_category(
    category_id: str,
    db: Annotated[Client, Depends(get_supabase_client)],
    _: CurrentUserDep,
) -> CategoryOut:
    cat = CategoryService(db).get(category_id)
    if not cat:
        raise _not_found()
    return cat


@router.post("", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
async def create_category(
    data: CategoryCreate,
    db: Annotated[Client, Depends(get_supabase_client)],
    _: SysAdmin,
) -> CategoryOut:
    return CategoryService(db).create(data)


@router.patch("/{category_id}", response_model=CategoryOut)
async def update_category(
    category_id: str,
    data: CategoryUpdate,
    db: Annotated[Client, Depends(get_supabase_client)],
    _: SysAdmin,
) -> CategoryOut:
    return CategoryService(db).update(category_id, data)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: str,
    db: Annotated[Client, Depends(get_supabase_client)],
    _: SysAdmin,
) -> None:
    CategoryService(db).delete(category_id)