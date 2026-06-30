from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client

from app.core.auth import get_current_user, require_roles
from app.core.models import CurrentUser, Role
from app.core.supabase_client import get_supabase_client
from app.modules.payment_methods.schemas import (
    PaymentMethodCreate,
    PaymentMethodOut,
    PaymentMethodUpdate,
)
from app.modules.payment_methods.service import PaymentMethodService

router = APIRouter(prefix="/payment-methods", tags=["Payment Methods"])

CurrentUserDep = Annotated[CurrentUser, Depends(get_current_user)]
SysAdmin = Annotated[CurrentUser, Depends(require_roles(Role.SYSTEM_ADMIN))]


def _not_found() -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not found")


@router.get("", response_model=list[PaymentMethodOut])
async def list_payment_methods(
    db: Annotated[Client, Depends(get_supabase_client)],
    _: CurrentUserDep,
) -> list[PaymentMethodOut]:
    return PaymentMethodService(db).list()


@router.get("/{method_id}", response_model=PaymentMethodOut)
async def get_payment_method(
    method_id: str,
    db: Annotated[Client, Depends(get_supabase_client)],
    _: CurrentUserDep,
) -> PaymentMethodOut:
    method = PaymentMethodService(db).get(method_id)
    if not method:
        raise _not_found()
    return method


@router.post("", response_model=PaymentMethodOut, status_code=status.HTTP_201_CREATED)
async def create_payment_method(
    data: PaymentMethodCreate,
    db: Annotated[Client, Depends(get_supabase_client)],
    _: SysAdmin,
) -> PaymentMethodOut:
    return PaymentMethodService(db).create(data)


@router.patch("/{method_id}", response_model=PaymentMethodOut)
async def update_payment_method(
    method_id: str,
    data: PaymentMethodUpdate,
    db: Annotated[Client, Depends(get_supabase_client)],
    _: SysAdmin,
) -> PaymentMethodOut:
    return PaymentMethodService(db).update(method_id, data)


@router.delete("/{method_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_payment_method(
    method_id: str,
    db: Annotated[Client, Depends(get_supabase_client)],
    _: SysAdmin,
) -> None:
    PaymentMethodService(db).delete(method_id)