
from supabase import Client

from app.core.errors import AppError
from app.modules.cash_accounts.repository import CashAccountRepository
from app.modules.cash_accounts.schemas import (
    CashAccountCreate,
    CashAccountOut,
    CashAccountUpdate,
)


class CashAccountService:
    def __init__(self, db: Client) -> None:
        self.repo = CashAccountRepository(db)

    def list(self) -> list[CashAccountOut]:
        return [CashAccountOut(**row) for row in self.repo.list()]

    def get(self, account_id: str) -> CashAccountOut | None:
        row = self.repo.get(account_id)
        return CashAccountOut(**row) if row else None

    def create(self, data: CashAccountCreate) -> CashAccountOut:
        payload = data.model_dump()
        payload["account_type"] = data.account_type.value
        return CashAccountOut(**self.repo.create(payload))

    def update(self, account_id: str, data: CashAccountUpdate) -> CashAccountOut:
        payload = data.model_dump(exclude_unset=True)
        if not payload:
            raise AppError("No fields to update")
        if data.account_type is not None:
            payload["account_type"] = data.account_type.value
        row = self.repo.update(account_id, payload)
        if not row:
            raise AppError("Cash account not found", 404)
        return CashAccountOut(**row)

    def delete(self, account_id: str) -> None:
        if self.repo.delete(account_id) == 0:
            raise AppError("Cash account not found", 404)