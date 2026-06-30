
from supabase import Client

from app.core.errors import AppError
from app.modules.payment_methods.repository import PaymentMethodRepository
from app.modules.payment_methods.schemas import (
    PaymentMethodCreate,
    PaymentMethodOut,
    PaymentMethodUpdate,
)


class PaymentMethodService:
    def __init__(self, db: Client) -> None:
        self.repo = PaymentMethodRepository(db)

    def list(self) -> list[PaymentMethodOut]:
        return [PaymentMethodOut(**row) for row in self.repo.list()]

    def get(self, method_id: str) -> PaymentMethodOut | None:
        row = self.repo.get(method_id)
        return PaymentMethodOut(**row) if row else None

    def create(self, data: PaymentMethodCreate) -> PaymentMethodOut:
        return PaymentMethodOut(**self.repo.create(data.model_dump()))

    def update(self, method_id: str, data: PaymentMethodUpdate) -> PaymentMethodOut:
        payload = data.model_dump(exclude_unset=True)
        if not payload:
            raise AppError("No fields to update")
        row = self.repo.update(method_id, payload)
        if not row:
            raise AppError("Payment method not found", 404)
        return PaymentMethodOut(**row)

    def delete(self, method_id: str) -> None:
        if self.repo.delete(method_id) == 0:
            raise AppError("Payment method not found", 404)