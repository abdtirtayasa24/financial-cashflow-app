from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query, status
from supabase import Client

from app.core.auth import get_current_user
from app.core.config import Settings, get_settings
from app.core.models import CurrentUser
from app.core.supabase_client import get_supabase_client
from app.modules.transactions.schemas import (
    AuditLogOut,
    ReviewAction,
    TransactionCreate,
    TransactionDirection,
    TransactionOut,
    TransactionStatus,
    TransactionUpdate,
)
from app.modules.transactions.service import TransactionService

router = APIRouter(prefix="/transactions", tags=["Transactions"])

UserDep = Annotated[CurrentUser, Depends(get_current_user)]
DbDep = Annotated[Client, Depends(get_supabase_client)]
SettingsDep = Annotated[Settings, Depends(get_settings)]


def _service(db: Client, settings: Settings) -> TransactionService:
    return TransactionService(db, settings)


@router.get("", response_model=list[TransactionOut])
async def list_transactions(
    db: DbDep,
    user: UserDep,
    settings: SettingsDep,
    date_from: Annotated[str | None, Query()] = None,
    date_to: Annotated[str | None, Query()] = None,
    department_id: Annotated[str | None, Query()] = None,
    category_id: Annotated[str | None, Query()] = None,
    cash_account_id: Annotated[str | None, Query()] = None,
    transaction_status: Annotated[TransactionStatus | None, Query(alias="status")] = None,
    direction: Annotated[TransactionDirection | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[TransactionOut]:
    filters = {
        "date_from": date_from,
        "date_to": date_to,
        "department_id": department_id,
        "category_id": category_id,
        "cash_account_id": cash_account_id,
        "status": transaction_status.value if transaction_status else None,
        "direction": direction.value if direction else None,
    }
    return _service(db, settings).list(filters, user, limit=limit, offset=offset)


@router.post("", response_model=TransactionOut, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    data: TransactionCreate,
    db: DbDep,
    user: UserDep,
    settings: SettingsDep,
) -> TransactionOut:
    return _service(db, settings).create(data, user)


@router.get("/{transaction_id}", response_model=TransactionOut)
async def get_transaction(
    transaction_id: str,
    db: DbDep,
    user: UserDep,
    settings: SettingsDep,
) -> TransactionOut:
    return _service(db, settings).get(transaction_id, user)


@router.patch("/{transaction_id}", response_model=TransactionOut)
async def update_transaction(
    transaction_id: str,
    data: TransactionUpdate,
    db: DbDep,
    user: UserDep,
    settings: SettingsDep,
) -> TransactionOut:
    return _service(db, settings).update(transaction_id, data, user)


@router.post("/{transaction_id}/submit", response_model=TransactionOut)
async def submit_transaction(
    transaction_id: str,
    db: DbDep,
    user: UserDep,
    settings: SettingsDep,
) -> TransactionOut:
    return _service(db, settings).submit(transaction_id, user)


@router.post("/{transaction_id}/approve", response_model=TransactionOut)
async def approve_transaction(
    transaction_id: str,
    db: DbDep,
    user: UserDep,
    settings: SettingsDep,
) -> TransactionOut:
    return _service(db, settings).approve(transaction_id, user)


@router.post("/{transaction_id}/reject", response_model=TransactionOut)
async def reject_transaction(
    transaction_id: str,
    data: ReviewAction,
    db: DbDep,
    user: UserDep,
    settings: SettingsDep,
) -> TransactionOut:
    return _service(db, settings).reject(transaction_id, data.reason, user)


@router.post("/{transaction_id}/void", response_model=TransactionOut)
async def void_transaction(
    transaction_id: str,
    data: ReviewAction,
    db: DbDep,
    user: UserDep,
    settings: SettingsDep,
) -> TransactionOut:
    return _service(db, settings).void(transaction_id, data.reason, user)


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    transaction_id: str,
    db: DbDep,
    user: UserDep,
    settings: SettingsDep,
) -> None:
    _service(db, settings).delete(transaction_id, user)


@router.get("/{transaction_id}/audit-logs", response_model=list[AuditLogOut])
async def list_audit_logs(
    transaction_id: str,
    db: DbDep,
    user: UserDep,
    settings: SettingsDep,
) -> list[dict[str, Any]]:
    return _service(db, settings).audit_logs(transaction_id, user)