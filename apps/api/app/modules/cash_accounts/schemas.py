from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class AccountType(StrEnum):
    CASH = "CASH"
    BANK = "BANK"
    EWALLET = "EWALLET"
    OTHER = "OTHER"


class CashAccountCreate(BaseModel):
    name: str
    account_type: AccountType
    opening_balance: float = Field(default=0, ge=0)
    opening_balance_date: str  # ISO date YYYY-MM-DD
    currency: str = "IDR"
    is_active: bool = True


class CashAccountUpdate(BaseModel):
    name: str | None = None
    account_type: AccountType | None = None
    opening_balance: float | None = Field(default=None, ge=0)
    opening_balance_date: str | None = None
    currency: str | None = None
    is_active: bool | None = None


class CashAccountOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="ignore")

    id: str
    name: str
    account_type: str
    opening_balance: float
    opening_balance_date: str
    currency: str
    is_active: bool
    created_at: str