from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class NotificationType(StrEnum):
    PENDING_APPROVAL = "PENDING_APPROVAL"
    RECURRING_DRAFT_READY = "RECURRING_DRAFT_READY"


class NotificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="ignore")

    id: str
    user_id: str
    type: NotificationType
    title: str
    message: str
    related_transaction_id: str | None = None
    is_read: bool
    created_at: str


class UnreadCountOut(BaseModel):
    count: int = Field(ge=0)


class MarkAllReadOut(BaseModel):
    updated: int = Field(ge=0)
