from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client

from app.core.auth import get_current_user, require_roles
from app.core.models import CurrentUser, Role
from app.core.supabase_client import get_supabase_client
from app.modules.departments.schemas import (
    DepartmentCreate,
    DepartmentOut,
    DepartmentUpdate,
)
from app.modules.departments.service import DepartmentService

router = APIRouter(prefix="/departments", tags=["Departments"])

CurrentUserDep = Annotated[CurrentUser, Depends(get_current_user)]
SysAdmin = Annotated[CurrentUser, Depends(require_roles(Role.SYSTEM_ADMIN))]


def _not_found() -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not found")


@router.get("", response_model=list[DepartmentOut])
async def list_departments(
    db: Annotated[Client, Depends(get_supabase_client)],
    _: CurrentUserDep,
) -> list[DepartmentOut]:
    return DepartmentService(db).list()


@router.get("/{department_id}", response_model=DepartmentOut)
async def get_department(
    department_id: str,
    db: Annotated[Client, Depends(get_supabase_client)],
    _: CurrentUserDep,
) -> DepartmentOut:
    dept = DepartmentService(db).get(department_id)
    if not dept:
        raise _not_found()
    return dept


@router.post("", response_model=DepartmentOut, status_code=status.HTTP_201_CREATED)
async def create_department(
    data: DepartmentCreate,
    db: Annotated[Client, Depends(get_supabase_client)],
    _: SysAdmin,
) -> DepartmentOut:
    return DepartmentService(db).create(data)


@router.patch("/{department_id}", response_model=DepartmentOut)
async def update_department(
    department_id: str,
    data: DepartmentUpdate,
    db: Annotated[Client, Depends(get_supabase_client)],
    _: SysAdmin,
) -> DepartmentOut:
    return DepartmentService(db).update(department_id, data)


@router.delete("/{department_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_department(
    department_id: str,
    db: Annotated[Client, Depends(get_supabase_client)],
    _: SysAdmin,
) -> None:
    DepartmentService(db).delete(department_id)