from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TransactionDirection(StrEnum):
    INFLOW = "INFLOW"
    OUTFLOW = "OUTFLOW"


class TransactionStatus(StrEnum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    VOIDED = "VOIDED"


class TransactionBase(BaseModel):
    """Editable transaction fields (valid while DRAFT or REJECTED)."""

    transaction_date: str  # ISO date YYYY-MM-DD
    direction: TransactionDirection
    amount: float = Field(gt=0)
    cash_account_id: str
    department_id: str
    category_id: str
    payment_method_id: str = Field(min_length=1)
    counterparty_name: str | None = None
    reference_no: str | None = None
    description: str | None = None


class TransactionCreate(TransactionBase):
    """Creating a transaction always starts in DRAFT."""


class TransactionUpdate(BaseModel):
    """Partial update of editable fields (DRAFT/REJECTED only)."""

    transaction_date: str | None = None
    direction: TransactionDirection | None = None
    amount: float | None = Field(default=None, gt=0)
    cash_account_id: str | None = None
    department_id: str | None = None
    category_id: str | None = None
    payment_method_id: str | None = None
    counterparty_name: str | None = None
    reference_no: str | None = None
    description: str | None = None


class TransactionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="ignore")

    id: str
    transaction_no: str
    transaction_date: str
    direction: str
    amount: float
    currency: str
    exchange_rate: float
    base_amount: float
    cash_account_id: str
    department_id: str
    category_id: str
    payment_method_id: str | None = None
    counterparty_name: str | None = None
    reference_no: str | None = None
    description: str | None = None
    status: str
    created_by: str
    submitted_at: str | None = None
    reviewed_by: str | None = None
    reviewed_at: str | None = None
    rejection_reason: str | None = None
    void_reason: str | None = None
    created_at: str
    updated_at: str


class AuditLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="ignore")

    id: str
    transaction_id: str
    actor_user_id: str
    actor_name: str | None = None
    action: str
    old_value: dict[str, Any] | None = None
    new_value: dict[str, Any] | None = None
    reason: str | None = None
    created_at: str


class TransactionFilters(BaseModel):
    """Query-string filters for the transaction list."""

    date_from: str | None = None
    date_to: str | None = None
    department_id: str | None = None
    category_id: str | None = None
    cash_account_id: str | None = None
    status: TransactionStatus | None = None
    direction: TransactionDirection | None = None


class ReviewAction(BaseModel):
    """Body for reject / void actions — a reason is required."""

    reason: str = Field(min_length=1)

    @field_validator("reason")
    @classmethod
    def reason_must_not_be_blank(cls, value: str) -> str:
        reason = value.strip()
        if not reason:
            raise ValueError("Reason is required")
        return reason
