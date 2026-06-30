from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client

from app.core.auth import get_current_user, require_roles
from app.core.models import CurrentUser, Role
from app.core.supabase_client import get_supabase_client
from app.modules.cash_accounts.schemas import (
    CashAccountCreate,
    CashAccountOut,
    CashAccountUpdate,
)
from app.modules.cash_accounts.service import CashAccountService

router = APIRouter(prefix="/cash-accounts", tags=["Cash Accounts"])

CurrentUserDep = Annotated[CurrentUser, Depends(get_current_user)]
SysAdmin = Annotated[CurrentUser, Depends(require_roles(Role.SYSTEM_ADMIN))]


def _not_found() -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not found")


@router.get("", response_model=list[CashAccountOut])
async def list_cash_accounts(
    db: Annotated[Client, Depends(get_supabase_client)],
    _: CurrentUserDep,
) -> list[CashAccountOut]:
    return CashAccountService(db).list()


@router.get("/{account_id}", response_model=CashAccountOut)
async def get_cash_account(
    account_id: str,
    db: Annotated[Client, Depends(get_supabase_client)],
    _: CurrentUserDep,
) -> CashAccountOut:
    account = CashAccountService(db).get(account_id)
    if not account:
        raise _not_found()
    return account


@router.post("", response_model=CashAccountOut, status_code=status.HTTP_201_CREATED)
async def create_cash_account(
    data: CashAccountCreate,
    db: Annotated[Client, Depends(get_supabase_client)],
    _: SysAdmin,
) -> CashAccountOut:
    return CashAccountService(db).create(data)


@router.patch("/{account_id}", response_model=CashAccountOut)
async def update_cash_account(
    account_id: str,
    data: CashAccountUpdate,
    db: Annotated[Client, Depends(get_supabase_client)],
    _: SysAdmin,
) -> CashAccountOut:
    return CashAccountService(db).update(account_id, data)


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cash_account(
    account_id: str,
    db: Annotated[Client, Depends(get_supabase_client)],
    _: SysAdmin,
) -> None:
    CashAccountService(db).delete(account_id)