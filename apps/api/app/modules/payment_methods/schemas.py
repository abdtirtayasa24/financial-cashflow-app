from pydantic import BaseModel, ConfigDict


class PaymentMethodCreate(BaseModel):
    name: str
    is_active: bool = True


class PaymentMethodUpdate(BaseModel):
    name: str | None = None
    is_active: bool | None = None


class PaymentMethodOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="ignore")

    id: str
    name: str
    is_active: bool